"""Supplement tables, claim map, and complete artifact provenance."""
import hashlib
import json
from pathlib import Path
import build_all as b

def main():
    d=b.load()
    labels=sorted({r['label'] for r in d['cross_classes']})
    names=['Bing search','MDN documentation','GitHub repository','Wikipedia article','YouTube search','YouTube playback']
    print('Class order:',labels)
    rows=[]
    for p,short in [('SHADOWSOCKS','SS to VL'),('VLESS','VL to SS')]:
        for label,name in zip(labels,names):
            values=[b.select(d['cross_classes'],source_protocol=p,domain='target',arm=a,label=label) for a in ['A','B','F','H','E']]
            assert all(v['support']==20 for v in values)
            rows.append([short,name]+[f"{v['f1']:.4f}" for v in values])
    b.table('cross_classes',['Direction','Class','A','B','F','H',r'$E_s$'],rows,'llrrrrr')
    claims=[
      ('C1','measurement','Descriptive repeated changes','transform',{'cohort':'0916_240','level':'all'},'No protocol causal attribution; no ICC or equivalence claim'),
      ('C2','measurement','Recoverability and task utility differ','joint',{'protocol':'pooled'},'Finite fixed learners; not mutual information'),
      ('C3','evaluation','Direct transfer degrades; statistical calibration partially restores','ah',{'protocol':'pooled'},'Seen deployments and held-out contents'),
      ('C4','evaluation','Exact pairing beats cyclic mismatch under statistical objective','contrasts',{'contrast':'C-D'},'Does not prove exact pairing is necessary under all objectives'),
      ('C5','evaluation','Decision-aware objective improves task score despite greater statistical MSE','decision_fidelity',{'split':'test'},'Same capacity; no universal recovery-performance relationship'),
      ('C6','evaluation','Center target changes fidelity without clear pooled F1 superiority/inferiority','fidelity',{'split':'test'},'No equivalence margin; deployed directions differ'),
      ('C7','evaluation','Cross-deployment benefit is directional','cross_contrasts',{'domain':'target'},'Fit-time isolation, not historically unseen external test'),
      ('C8','evaluation','Source-entrance model also shifts','cross',{'arm':'A'},'Reference, not upper bound or causal factor isolation'),
      ('C9','evaluation','Repairs coexist with introduced errors','cross_flips',{'domain':'target'},'Same-visit transitions only'),
    ]
    ledger=[]
    for id,section,claim,key,selector,limit in claims:
        rr=[r for r in d[key] if all(r.get(k)==v for k,v in selector.items())]
        assert rr
        ledger.append({'id':id,'section':section,'claim':claim,'source':b.SOURCES[key],'selector':selector,'evidence':rr,'boundary':limit})
    (b.EVIDENCE/'claim_ledger.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8')
    manifest=json.loads((b.EVIDENCE/'artifact_manifest.json').read_text())
    reports=['0916-dataset-and-experiments-summary-20260917.md','0916-transformation-replication-results-20260918.md','0916-group-anchor-controlled-diagnostics-results-20260919.md','0916-source-classifier-cross-side-transfer-results.md','0916-source-decision-aware-calibration-results.md','0916-source-score-hierarchy-center-control-results.md','0916-source-calibration-cross-deployment-results.md','0916-natural-pair-ssl-results-20260918.md','0916-MLP-detailed-experiment-record-20260918.md']
    manifest['context_reports']={f'docs/{p}':hashlib.sha256((b.ROOT/'docs'/p).read_bytes()).hexdigest() for p in reports}
    manifest['audit_sources']={}
    for folder in ['source-transfer-0916','source-decision-calibration-0916','source-center-control-0916','source-calibration-cross-deployment-0916','group-anchor-diagnostics-0916']:
        path=b.ROOT/'outputs'/folder/'run-01/audit/validation.json'
        manifest['audit_sources'][str(path.relative_to(b.ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    manifest['figure_sources']={
       'transformations':['transform'],'group-utility':['joint'],
       'ah-performance':['ah'],'paired-contrasts':['contrasts'],
       'recovery-task':['decision_fidelity','fidelity','ah'],
       'cross-deployment':['cross'],'decision-changes':['cross_flips']}
    manifest['manuscript_and_generated_files']={str(p.relative_to(b.PAPER)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.PAPER.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.drawio','.pdf'] and 'build' not in p.parts}
    (b.EVIDENCE/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Supplement table and nine claims saved with source hashes.')

if __name__=='__main__':main()
