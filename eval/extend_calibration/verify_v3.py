"""Independent v3 event, fragment provenance and CUDA verification; no fitting."""
from pathlib import Path
import sys
import struct
import importlib.util
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,fs_path,file_hash
from proxy_analysis.parsing import PcapNgReader
from proxy_analysis.parsing.packet_decoder import _strip_link_header
spec=importlib.util.spec_from_file_location('v1_verify',ROOT/'eval/extend_calibration/verify_extraction.py')
v1=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1)
BASE=ROOT/'outputs/extend-calibration-20260930/run-01';OLD=BASE/'extraction-01';NEW=BASE/'extraction-03'


def main():
    out=NEW/'verification-01';out.mkdir(exist_ok=True)
    assert not (out/'verification.json').exists()
    pool=pd.read_parquet(OLD/'metadata-qualified-pool.parquet')
    w=pd.read_parquet(NEW/'full-W-features.parquet').set_index(['session_id','side'])
    t=pd.read_parquet(NEW/'full-T-features.parquet').set_index(['session_id','side'])
    assert len(w)==len(t)==1200
    provenance_rows=[];rows=[]
    for n,row in enumerate(pool.to_dict('records'),1):
        sid=row['session_id'];folder=NEW/'sessions'/sid
        r=read(folder/'complete.json');pairs=read(folder/'T-pairs.json')
        common={p['logical_id'] for p in pairs if p['common_valid_nonempty']}
        te=pd.read_parquet(folder/'T-newbyte-events.parquet')
        for side,filename in [('pre','tun.pcap'),('post','phys.pcap')]:
            events=pd.read_parquet(folder/f'{side}-W-events.parquet')
            assert np.array_equal(v1.recount(events,'payload_bytes'),w.loc[(sid,side),v1.WCOLS].to_numpy(dtype='int64'))
            selected=te if te.empty else te[te.side.eq(side)&te.logical_id.isin(common)]
            assert np.array_equal(v1.recount(selected,'new_bytes',True),t.loc[(sid,side),v1.TCOLS].to_numpy(dtype='int64'))
            assert t.loc[(sid,side),'F']==len(common)
            assert events.timestamp_ns.between(r['start_ns'],r['end_ns'],inclusive='left').all()
            reassembly=folder/f'{side}-reassembly.json'
            if reassembly.exists():
                prov=read(reassembly)['provenance']
                if prov:
                    by_ordinal={ordinal:(j,p) for j,p in enumerate(prov) for ordinal in p['source_ordinals']}
                    assert len(by_ordinal)==sum(len(p['source_ordinals']) for p in prov)
                    pieces={j:[] for j in range(len(prov))}
                    base=(fs_path(ROOT/'Datasets/extend')/row['manifest_relative']).parent
                    assert file_hash(base/'raw'/filename)==r['input_hashes']['raw/'+filename]
                    for rec in PcapNgReader(base/'raw'/filename):
                        if rec.packet_ordinal in by_ordinal:
                            j,p=by_ordinal[rec.packet_ordinal];ip=_strip_link_header(rec.link_type,rec.packet_data)
                            length,ident,flags=struct.unpack('!HHH',ip[2:8]);ihl=(ip[0]&15)*4
                            pieces[j].append(((flags&8191)*8,ip[ihl:length],bool(flags&8192),rec.timestamp_ns,ident,ip[12:20]))
                    indexed=events.set_index('raw_packet_ordinal')
                    for j,p in enumerate(prov):
                        parts=pieces[j];assert len(parts)==len(p['source_ordinals'])
                        assert len({(a[4],a[5]) for a in parts})==1
                        final={offset+len(payload) for offset,payload,more,*_ in parts if not more}
                        assert len(final)==1
                        # Independent exact byte-position coverage with equality for overlaps.
                        merged={}
                        for offset,payload,*_ in parts:
                            for k,value in enumerate(payload,offset):
                                assert k not in merged or merged[k]==value
                                merged[k]=value
                        assert set(merged)==set(range(next(iter(final))))
                        # Observed completed fragmented datagrams in this cohort are UDP.
                        assert p['transport_payload_bytes']==len(merged)-8
                        assert p['complete_ns']==max(a[3] for a in parts)
                        if p['completion_ordinal'] in indexed.index:
                            assert indexed.loc[p['completion_ordinal'],'payload_bytes']==p['transport_payload_bytes']
                            assert indexed.loc[p['completion_ordinal'],'timestamp_ns']==p['complete_ns']
                    provenance_rows.append({'session_id':sid,'side':side,'datagrams':len(prov),
                        'source_packets':len(by_ordinal),'independent_byte_coverage_passed':True})
            rows.append({'session_id':sid,'side':side,'W_events':len(events),'T_events':len(selected),'recount_equal':True})
        if n%100==0:print(f'v3 independent verification {n}/600',flush=True)
    sys.path.insert(0,str(ROOT/'eval/hy2_carrier_calibration'))
    import window_model as wm
    from proxy_analysis.feasible_summary_calibration import model as tm
    import torch
    a=w[v1.WCOLS].to_numpy(dtype='int64');wd,_=wm.decode(wm.encode(a))
    assert wd.is_cuda and np.array_equal(a,wd.cpu().numpy())
    active=t[t.F.gt(0)];a=active[v1.TCOLS].to_numpy(dtype='int64');td,_=tm.decode(tm.encode(a),active.F.to_numpy())
    assert td.is_cuda and np.array_equal(a,td.cpu().numpy())
    torch.cuda.synchronize()
    pd.DataFrame(rows).to_parquet(out/'event-recounts.parquet',index=False)
    write(out/'fragment-source-replay.json',provenance_rows)
    oldw=pd.read_parquet(BASE/'extraction-02/full-W-features.parquet').set_index(['session_id','side'])
    delta=w[v1.WCOLS]-oldw[v1.WCOLS]
    delta.reset_index().to_parquet(out/'W-change-from-v2.parquet',index=False)
    cv=pd.read_parquet(NEW/'full-coverage.parquet')
    meta=pool[['session_id','protocol','content_id','label','repetition']].merge(cv[['session_id','W_gate_passed','review_reasons']],on='session_id',validate='one_to_one')
    catalog=NEW/'catalog-01';catalog.mkdir(exist_ok=True)
    files=[]
    for track,frame,cols in [('W',w,v1.WCOLS),('T',active,v1.TCOLS+['F'])]:
        f=frame.reset_index().merge(meta,on='session_id',validate='many_to_one');f['training_eligible']=False
        f['status']='candidate_only; capture_scope_and_epoch_isolation_not_released'
        path=catalog/f'{track}-candidate-features.parquet';f.to_parquet(path,index=False)
        files.append({'file':path.name,'rows':len(f),'numeric_model_allowlist':cols,'sha256':file_hash(path)})
    write(catalog/'manifest.json',{'training_allowed':False,'files':files,'metadata_is_not_model_input':True})
    write(out/'verification.json',{'visits':600,'independent_event_counts':True,'fragment_byte_provenance':True,
        'W_cuda_roundtrip_rows':len(w),'T_cuda_roundtrip_rows':len(active),'cuda':torch.cuda.get_device_name(0),
        'changed_W_sides':int(delta.ne(0).any(axis=1).sum()),'training_allowed':False,
        'independent_raw_transport_parser_replay':False,'source_code_sha256':file_hash(Path(__file__))})


if __name__=='__main__':main()

