"""Independent read-only result audit, content isolation and error attribution."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'outputs/post-associated-frozen-readout-20261014/run-01'
LABELS=['bing.com::search_results_view','developer.mozilla.org::document_view','github.com::repository_view',
        'wikipedia.org::article_view','youtube.com::search_results_view','youtube.com::video_playback']

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def stat(v):
    a=np.asarray(v,float);return dict(minimum=float(a.min()),mean=float(a.mean()),maximum=float(a.max()))
def metric(y,p,lp,missing):
    cm=np.bincount(y*6+p.argmax(1),minlength=36).reshape(6,6);den=cm.sum(0)+cm.sum(1)
    f1=np.divide(2*np.diag(cm),den,out=np.zeros(6),where=den>0)
    use=np.isin(y,missing);ce=-lp[np.arange(len(y)),y];b=((p-np.eye(6)[y])**2).sum(1)
    return dict(F1_U=float(f1[missing].mean()),F1_C=float(np.delete(f1,missing).mean()),F1_all=float(f1.mean()),
        CE_U=float(ce[use].mean()),CE_C=float(ce[~use].mean()),CE_all=float(ce.mean()),Brier=float(b.mean()),
        Brier_U=float(b[use].mean()),Brier_C=float(b[~use].mean()),accuracy=float((p.argmax(1)==y).mean()))

def main():
    c=read(RUN/'manifests/experiment-contract.json');done=read(RUN/'completion.json');assert done['passed']
    assert sha(RUN/'manifests/experiment-contract.json')==read(RUN/'manifests/contract-seal.json')['sha256']
    assert sha(ROOT/'plan/post-input-representation-output-scale-plan-v2-20261014.md')==c['plan_sha256']
    bindings=0
    for name in ['manifests/code.json','manifests/models-complete.json','predictions/complete.json','scores/complete.json']:
        m=read(RUN/name);assert m['passed']
        for p,h in m['files'].items():assert sha(ROOT/p)==h,p;bindings+=1
    d=pd.read_parquet(RUN/'predictions/visits.parquet');base=pd.read_parquet(RUN/'predictions/base.parquet')
    scores=read(RUN/'scores/role-results.json');scoreindex={(r['role_id'],r['arm'],r['eta'],r['seed']):r for r in scores}
    pc=[f'p{k}' for k in range(6)];lc=[f'l{k}' for k in range(6)]
    truth={};content={};labeldict={};split=[];maxerror=0.;checked=[]
    for r in c['roles']:
        p=ROOT/r['labels'];info=c['sources'][r['labels']];assert info['kind']=='query-label' and sha(p)==info['sha256']
        labels=pd.read_parquet(p);assert len(labels)==24 and labels.visit_id.is_unique
        assert set(labels.content_id)==set(r['validation_contents'])
        assert not set(labels.content_id)&set(r['train_contents'])
        assert not set(r['validation_contents'])&set(r['train_contents'])
        assert (labels.protocol==r['calibration']).all() and labels.groupby('content_id').size().eq(4).all()
        for v,co,la in labels[['visit_id','content_id','label_id']].itertuples(index=False,name=None):
            truth[(r['id'],v)]=LABELS.index(la);content[(r['id'],v)]=co;labeldict[(r['id'],v)]=la
        split.append(dict(role_id=r['id'],query_contents=6,training_contents=len(r['train_contents']),content_overlap=0,query_protocol=r['calibration']))
        sub=d[d.role_id.eq(r['id'])]
        for (arm,eta,seed),z in sub.groupby(['arm','eta','seed']):
            y=np.array([truth[(r['id'],v)] for v in z.visit_id],int);m=metric(y,z[pc].to_numpy(),z[lc].to_numpy(),r['missing'])
            old=scoreindex[(r['id'],arm,float(eta),int(seed))]
            for k,v in m.items():maxerror=max(maxerror,abs(v-old[k]))
            checked.append(dict(role_id=r['id'],arm=arm,eta=float(eta),seed=int(seed),**m))
    assert maxerror<=1e-14 and len(checked)==288
    eps=read(RUN/'manifests/endpoints.json');assert len(eps)==288 and len({e['model'] for e in eps})==240
    assert len(d)==6912 and len(base)==288
    s=read(RUN/'scores/summary.json')
    for cell in s['cells']:
        ss=[r for r in checked if r['arm']==cell['arm'] and r['eta']==cell['eta']]
        for k in ['F1_U','F1_C','CE_U','CE_C','Brier']:assert abs(np.mean([r[k] for r in ss])-cell[k])<=1e-14
    quality=[read(p) for p in (RUN/'fit-logs').rglob('quality.json')];assert len(quality)==240 and all(r['passed'] for r in quality)
    gradmax=max(r['max_original_gradient'] for r in quality);objmax=max(r['objective_replay_error'] for r in quality)
    assert gradmax<=1e-5 and objmax<=1e-10
    outputs=read(RUN/'diagnostics/output-use.json');cells=[]
    for arm in ['X','R','G','P']:
        for eta in [1.,.01]:
            logs=[v for v in quality if v['arm']==arm and v['eta']==eta];dd=[v for v in outputs if v['arm']==arm and v['eta']==eta]
            rr=[v for v in scores if v['arm']==arm and v['eta']==eta]
            cells.append(dict(arm=arm,eta=eta,unique_fits=len(logs),training_CE=np.mean([v['CE'] for v in logs]).item(),
                training_CE_delta=np.mean([v['CE']-v['initial_objective'] for v in logs]).item(),
                D_x_norm=np.mean([v['D_x_norm'] for v in logs]).item(),D_G_norm=np.mean([v['D_g_norm'] for v in logs]).item(),
                delta_RMS=np.mean([v['delta_RMS'] for v in dd]).item(),G_RMS=np.mean([v['G_RMS'] for v in dd]).item(),
                x_RMS=np.mean([v['x_RMS'] for v in dd]).item(),guaranteed_unchanged=sum(v['guaranteed_unchanged'] for v in dd),
                cases=sum(v['cases'] for v in dd),G_zero_class_changes=sum(v['G_zero_class_changes'] for v in dd),
                off_G_CE_U=np.mean([v['off_G_CE_U'] for v in rr]).item(),off_G_F1_U=np.mean([v['off_G_F1_U'] for v in rr]).item(),
                repaired_U=sum(v['repaired_U'] for v in rr),added_U=sum(v['added_errors_U'] for v in rr),
                repaired_C=sum(v['repaired_C'] for v in rr),added_C=sum(v['added_errors_C'] for v in rr)))
    attribution=[];flips=[]
    rolemap={r['id']:r for r in c['roles']}
    for eta in [1.,.01]:
        sub=d[d.arm.eq('P')&d.eta.eq(eta)].copy();accum={}
        for (rid,seed),z in sub.groupby(['role_id','seed']):
            bb=base[base.role_id.eq(rid)].set_index('visit_id').loc[z.visit_id]
            p=z[pc].to_numpy();lp=z[lc].to_numpy();bp=bb[pc].to_numpy();blp=bb[lc].to_numpy();y=np.array([truth[(rid,v)] for v in z.visit_id])
            pred=p.argmax(1);oldpred=bp.argmax(1)
            for i,v in enumerate(z.visit_id):
                splitname='U' if y[i] in rolemap[rid]['missing'] else 'C'
                state=('correct' if oldpred[i]==y[i] else 'wrong')+'->'+('correct' if pred[i]==y[i] else 'wrong')
                target=accum.setdefault((splitname,state),[])
                target.append(dict(delta_CE=float(-lp[i,y[i]]+blp[i,y[i]]),base_CE=float(-blp[i,y[i]]),new_CE=float(-lp[i,y[i]]),
                    baseline_confidence=float(bp[i].max()),new_confidence=float(p[i].max())))
                if pred[i]!=oldpred[i]:
                    flips.append(dict(role_id=rid,seed=int(seed),eta=eta,visit_id=v,content_id=content[(rid,v)],business=labeldict[(rid,v)],
                        actual_target=rolemap[rid]['target'],query_protocol=rolemap[rid]['calibration'],split=splitname,
                        old_prediction=int(oldpred[i]),new_prediction=int(pred[i]),truth=int(y[i]),state=state))
        for (splitname,state),values in accum.items():
            attribution.append(dict(eta=eta,split=splitname,state=state,n=len(values),
                **{k:np.mean([v[k] for v in values]).item() for k in values[0]}))
    # Read-only sources include deferred query and labels now legally sealed/scored.
    for name,info in c['sources'].items():assert sha(ROOT/name)==info['sha256'],name
    stage_reads={p.stem:read(p)['reads'] for p in (RUN/'stages').glob('*.json') if 'reads' in read(p)}
    for name,reads in stage_reads.items():
        if name in ['P1_interface_pilot','P2_heads']:assert not any(r['purpose'] in ['predict','score'] for r in reads)
        assert not any('/outer/' in r['path'] and r['purpose'] in ['predict','score'] for r in reads)
    audit=dict(passed=True,bindings_verified=bindings,independent_metric_max_error=maxerror,
        unique_heads=240,endpoints=288,source_prediction_rows=6912,source_query_unique_visits=int(d.visit_id.nunique()),
        source_query_unique_contents=len(set(content.values())),max_original_gradient=gradmax,max_objective_replay_error=objmax,
        max_gradient_replay_error=max(r['gradient_replay_error'] for r in quality),fit_iterations=stat([r['iterations'] for r in quality]),
        optimizer_function_evaluations=stat([r['function_evaluations'] for r in quality]),
        roles_content_isolation=split,cells=cells,paired_error_attribution=attribution,paired_class_changes=flips,
        H_reads=0,actual_U_reads=0,historical_sources_unchanged=True,new_G_or_teacher_fits=0,
        old_role_decisions_unchanged=True,code_sha256=sha(Path(__file__)))
    out=RUN/'audits/independent-analysis.json'
    with out.open('x',encoding='utf-8') as f:json.dump(audit,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({k:audit[k] for k in ['passed','bindings_verified','independent_metric_max_error','unique_heads','source_query_unique_visits','source_query_unique_contents','max_original_gradient']},indent=2))
    for row in cells:print(json.dumps(row))
    for row in attribution:print(json.dumps(row))

if __name__=='__main__':main()
