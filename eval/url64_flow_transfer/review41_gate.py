"""Report a conservative selection proposal, never apply it to training."""
from collections import defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from proxy_analysis.extend_calibration.audit import read,write,fs_path,path_identity,file_hash
BASE=ROOT/'outputs/url64-flow-transfer-extend/run-01/approved41-01'


def proposed_entities(index, evidence):
    by_path={r['path_hash']:r for r in evidence}
    keep=set()
    for ident,paths in index.items():
        hashes={path_identity(p) for p in paths}
        # A changing/multiple physical-path entity is not silently merged.
        if len(hashes)!=1:continue
        r=by_path.get(next(iter(hashes)))
        if r and r['positive_packets']>0 and r['syn_count']==1 and len(r['entity_ids'])==1 and r['bad_packets']==0:
            keep.add(ident)
    return keep


def main():
    out=BASE/'conservative-proposal-01';assert not (out/'summary.json').exists()
    pool=pd.read_parquet(BASE/'candidate-visits.parquet');rows=[]
    for r in pool.to_dict('records'):
        sid=r['session_id'];scope=read(BASE/'private-audit'/f'{sid}.json')
        audit=read(BASE/'raw-audit-01/sessions'/f'{sid}.json')
        keep={side:proposed_entities(scope[side+'_index'],[p for p in audit['paths'] if p['side']==side]) for side in ['pre','post']}
        # Calibration pairing availability is inspected only in C, never used
        # to prune U or H. It is not byte-integrity qualification yet.
        pairs=None
        if r['role_pool']=='C':
            base=(fs_path(ROOT/'Datasets/extend')/r['manifest_relative']).parent
            pairs=sum(f.get('conn_id') in keep['pre'] and (f.get('carrier_binding') or {}).get('carrier_id') in keep['post']
                      for f in read(base/'analysis/flow-index.json')['items'])
        rows.append({'session_id':sid,'protocol':r['protocol'],'role_pool':r['role_pool'],
                     'pre_proposed_entities':len(keep['pre']),'post_proposed_entities':len(keep['post']),
                     'C_metadata_pair_candidates':pairs})
    frame=pd.DataFrame(rows);out.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(out/'visit-counts.parquet',index=False)
    counts=[]
    for (role,protocol),g in frame.groupby(['role_pool','protocol']):
        counts.append({'role_pool':role,'protocol':protocol,'visits':len(g),
                       'pre_entities':int(g.pre_proposed_entities.sum()),'post_entities':int(g.post_proposed_entities.sum()),
                       'minimum_pre_entities':int(g.pre_proposed_entities.min()),'minimum_post_entities':int(g.post_proposed_entities.min()),
                       'minimum_C_metadata_pair_candidates':int(g.C_metadata_pair_candidates.min()) if role=='C' else None})
    summary={'status':'proposal_only_requires_confirmation','counts':counts,
             'zero_side_candidate_visits':int((frame.pre_proposed_entities.eq(0)|frame.post_proposed_entities.eq(0)).sum()),
             'zero_C_metadata_pair_visits':int(frame.C_metadata_pair_candidates.eq(0).sum()),
             'byte_integrity_and_UER_not_extracted':True,'training_allowed':False,'code_sha256':file_hash(Path(__file__))}
    write(out/'summary.json',summary);print(summary)


if __name__=='__main__':main()
