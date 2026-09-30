"""Minimal new-head reload audit; never reload the 135 old classifiers."""
from run import *

def verify():
    freeze();rows=[];folds=load('folds');base=load('tensor-manifest')
    for folder in sorted(OUT.glob('f*-Q*')):
        done=read(folder/'done.json');p=pd.read_parquet(folder/'predictions.parquet')
        assert done['cuda'] and done['encoder_unchanged'] and not done['test_pre']
        assert done['predictions_sha256']==digest(folder/'predictions.parquet')
        log=pd.read_parquet(folder/'training-log.parquet');assert log.step.tolist()==list(range(1,1001)) and np.isfinite(log.loss).all()
        fold=int(p.fold.iloc[0]);seed=int(p.seed.iloc[0]);device=setup(seed)
        tr=folds[(folds.fold==fold)&(folds.split=='train')];te=folds[(folds.fold==fold)&(folds.split=='test')]
        assert not set(tr.content_id)&set(te.content_id)
        assert not set(base[base.session_id.isin(tr.session_id)].uid)&set(base[base.session_id.isin(te.session_id)].uid)
        with np.load(folder/'embeddings.npz') as cache:
            assert cache['train_ids'].tolist()==tr.session_id.tolist()
            assert cache['test_ids'].tolist()==te.session_id.tolist()==p.session_id.tolist()
            x=torch.tensor(cache['test'],device=device);std=np.std(cache['train'],axis=0,ddof=1)
        state=torch.load(folder/'head.pt',map_location=device,weights_only=False)
        assert state['encoder_hash']==done['encoder_hash'] and state['contract']==digest(OUT/'contract.json')
        model=Hierarchy().to(device);head=model.head;head.load_state_dict(state['head']);head.eval()
        with torch.no_grad():v=torch.cat([head(part).softmax(1) for part in x.split(6)]).cpu().numpy()
        expected=p[PROBS].to_numpy();np.testing.assert_allclose(v,expected,atol=2e-5,rtol=2e-4)
        assert np.array_equal(v.argmax(1),p.prediction)
        rows.append({'job':folder.name,'fold':fold,'seed':seed,'arm':p.arm.iloc[0],
          'head_sha256':digest(folder/'head.pt'),'cache_sha256':digest(folder/'embeddings.npz'),
          'encoder_unchanged':True,'heldout_content_disjoint':True,'flow_disjoint':True,'device':'cuda',
          'same_decisions':True,'max_probability_delta':float(np.abs(v-expected).max()),
          'train_embedding_std_mean':float(std.mean()),'train_embedding_std_min':float(std.min()),
          'seconds':done['seconds'],'final_train_ce_nats':float(log.ce_nats.tail(100).mean())})
    assert len(rows)==75
    audit=save('probe-audit',pd.DataFrame(rows));write_json(OUT/'probe-audit.json',{'jobs':75,'all_passed':True,'device':torch.cuda.get_device_name(),'max_probability_delta':float(audit.max_probability_delta.max()),'total_job_seconds':float(audit.seconds.sum())})
    # Visit-label metrics and decision changes use no fitting.
    p=pd.read_parquet(OUT/'probe-oof.parquet');changes=[];content=[]
    for a,b in [('Q3','Q0'),('Q3','Q1'),('Q3','Q2'),('Q3','Q4')]:
        g=p[p.arm==a].merge(p[p.arm==b],on=['fold','seed','session_id','content_id','label_id','repetition','target'],suffixes=('_a','_b'),validate='one_to_one')
        g['state']=states(g.prediction_a,g.prediction_b,g.target)
        for seed,h in g.groupby('seed'):
            changes.append({'arm':a,'reference':b,'seed':seed,**{s:int((h.state==s).sum()) for s in ['both_correct','corrected','new_error','same_wrong','different_wrong']}})
        for (seed,c),h in g.groupby(['seed','content_id']):
            content.append({'arm':a,'reference':b,'seed':seed,'content_id':c,'corrected':int((h.state=='corrected').sum()),'new_error':int((h.state=='new_error').sum())})
    save('probe-decision-changes',pd.DataFrame(changes));save('probe-content-changes',pd.DataFrame(content))
    old=pd.read_parquet(FORMAL/'metrics-by-seed.parquet');new=pd.read_parquet(OUT/'probe-metrics.parquet')
    pairs=[]
    for source in range(1,5):
        a=new[new.arm==f'Q{source}'].set_index('seed');b=old[old.arm==f'L{source}'].set_index('seed')
        for seed in cfg()['seeds']:
            pairs.append({'ssl_source':f'L{source}','seed':seed,'frozen_f1':a.loc[seed,'macro_f1'],'finetuned_f1':b.loc[seed,'macro_f1'],'difference':b.loc[seed,'macro_f1']-a.loc[seed,'macro_f1']})
    save('frozen-versus-finetuned',pd.DataFrame(pairs))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,metric in zip(axes,['macro_f1','ce_bits']):
        for seed,g in new.groupby('seed'):ax.plot(g.arm,g[metric],marker='o',label=str(seed))
        ax.set_ylabel(metric);ax.grid(alpha=.2);ax.legend()
    fig.savefig(DOC/'figures/frozen-probes.png',dpi=160);plt.close(fig)
    with (DOC/'frozen-probe-results.md').open('a',encoding='utf-8') as f:
        f.write('\n\n## 冻结读出与旧微调的描述比较\n\n'+table(pd.DataFrame(pairs))+'\n\n![冻结探针](figures/frozen-probes.png)\n\n75个新增分类头在CUDA独立重载、改为6访问批次验证，决策全部一致；编码器冻结、内容及flow隔离全部通过。旧135模型未重复重放。详细审计见probe-audit.parquet。\n')
    write_json(OUT/'implementation-manifest.json',{'files':{str(p):digest(p) for p in Path(__file__).parent.glob('*.py')},'tests':str(ROOT/'tests/unit/test_record_time_localization.py'),'old_contract_unchanged':True})
    print(read(OUT/'probe-audit.json'),flush=True)

if __name__=='__main__':verify()
