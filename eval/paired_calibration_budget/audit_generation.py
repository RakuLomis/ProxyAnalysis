"""Audit only C/U training artifacts. Does not open evaluation packages."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *
from proxy_analysis.conditional_drift.common import illegal

def audit():
    for path,h in read(OUT/'worker-contract.json')['inputs'].items():assert sha(path)==h
    rows=[];fits=0;seconds=0.
    for folder in sorted((OUT/'generation').iterdir()):
        done=read(folder/'complete.json');bundle=TrainingBundle(OUT/'bundles'/folder.name);meta=bundle.manifest
        assert done['bundle_hash']==sha(bundle.path/'manifest.json')
        assert set(done['read_roles'])=={'C_pre','C_post','U_pre'} and done['cuda']
        for path,h in done['files'].items():assert sha(path)==h
        for kind in ['true','wrong']:
            pool=pd.read_parquet(folder/(kind+'-pool.parquet'));lookup=pool.set_index('session_id').content_id
            assert set(pool.session_id)==set(meta['C_sessions'])
            assert (pool.target_session_id.map(lookup)==pool.content_id).all()
            if kind=='true':assert (pool.target_session_id==pool.session_id).all()
            else:assert (pool.target_session_id!=pool.session_id).all() and pool.target_session_id.nunique()==len(pool)
        for kind,folds in read(folder/'residual-folds.json').items():
            assert len(folds)==len(meta['C_contents'])
            for fold in folds:
                assert fold['cuda'] and fold['held_content'] not in fold['fit_contents']
                assert set(fold['fit_contents'])==set(meta['C_contents'])-{fold['held_content']}
                assert set(fold['held_sessions']).issubset(set(meta['C_sessions']))
        total=0
        for seed in config()['seeds']:
            g=pd.read_parquet(folder/f'samples-{seed}.parquet');total+=len(g)
            assert set(g.session_id)==set(meta['U_sessions']) and set(g.C_hash)=={meta['C_hash']}
            assert 'label_id' not in g and not g.duplicated(['arm','session_id','view']).any()
            assert set(g.donor_session.dropna()).issubset(set(meta['C_sessions']))
            assert set(g.target_donor_session.dropna()).issubset(set(meta['C_sessions']))
            for record in g[NUMERIC].itertuples(index=False,name=None):assert not illegal(record[:6],record[6])
        fits+=done['ridge_fits'];seconds+=done['seconds']
        rows.append({'scenario':folder.name,'views':total,'only_C_donors':True,'U_content_unseen':True,'LOCO_C_only':True,'labels_not_read_by_generator':True,'cuda':True})
    assert len(rows)==120 and fits==3120
    save('generation-permission-audit',rows)
    write(OUT/'generation-permission-audit.json',{'passed':True,'scenarios':120,'ridge_fits':fits,'cuda':True,'task_seconds':seconds,'evaluation_packages_read':False,'views':sum(r['views'] for r in rows)})
    s=pd.read_parquet(OUT/'legality-summary.parquet')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=DOC/'figures';dest.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,dep in zip(axes,config()['deployments']):
        for arm,g in s[s.protocol==dep].groupby('arm'):ax.plot(g.k*6,g.first_invalid_rate*100,marker='o',label=arm)
        ax.axhline(10,color='red',linestyle='--',label='Frozen gate 10%');ax.set_title(dep);ax.set_xlabel('Paired calibration contents');ax.set_ylabel('First-invalid proposal rate (%)');ax.legend();ax.grid(alpha=.2)
    fig.savefig(dest/'legality-budget.png',dpi=160);plt.close(fig)
    print(read(OUT/'generation-permission-audit.json'),flush=True)

if __name__=='__main__':audit()
