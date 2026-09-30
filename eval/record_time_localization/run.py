"""Independent, frozen-contract error localization and CUDA frozen-head probes."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import json, hashlib, time, argparse
import numpy as np
import pandas as pd  # Load Arrow before torch on Windows.
from proxy_analysis.crosscontent.record_time_business.data import OUT as OLD, cfg, load, read, digest
from proxy_analysis.crosscontent.record_time_business.formal import FORMAL, View, write_json, ENCODER
from proxy_analysis.crosscontent.record_time_business.formal_report import scores
from proxy_analysis.crosscontent.record_time_business.engineering import setup, input_visits
from proxy_analysis.crosscontent.record_time_business.model import Hierarchy
from proxy_analysis.crosscontent.record_time_business.tensors import Store
import torch

OUT=ROOT/'outputs/record-time-localization-0916/run-01'
DOC=ROOT/'docs/record-time-business-0916/localization'
NAMES=['macro_f1','balanced_accuracy','ce_bits','brier']
PROBS=[f'p{i}' for i in range(6)]

def save(name, frame):
    frame.to_parquet(OUT/(name+'.parquet'),index=False)
    return frame

def table(frame):
    return frame.to_markdown(index=False,floatfmt='.6f')

def freeze():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    old=read(FORMAL/'contract.json')
    for p,h in old['files'].items():
        assert digest(p)==h, f'Frozen source changed: {p}'
    files=[Path(__file__),ROOT/'plan/record-time-business-localization-plan-20260926.md',
        FORMAL/'contract.json',FORMAL/'completion.json',FORMAL/'oof-predictions.parquet',
        FORMAL/'metrics-by-seed.parquet',FORMAL/'decision-changes.parquet',FORMAL/'paired-gains.parquet']
    for p in FORMAL.glob('*-ssl/final.pt'):
        assert digest(p)==read(p.parent/'done.json')['checkpoint_sha256']
        files.append(p)
    assert len(list(FORMAL.glob('*-ssl/final.pt')))==60
    for r in load('tensor-manifest').itertuples():assert digest(r.path)==r.sha256
    contract={'files':{str(p):digest(p) for p in files},'source_contract':old,
      'probe_sources':['Q0','Q1','Q2','Q3','Q4'],'steps':1000,'head':'65-32-ReLU-6',
      'device':'cuda','test_pre':False,'tuning':False,'bootstrap_seed':20260926}
    path=OUT/'contract.json'
    if path.exists():assert read(path)==contract,'Changed diagnostic contract'
    else:write_json(path,contract)

def states(a,b,target):
    gooda=a==target;goodb=b==target
    return np.select([gooda&goodb,gooda&~goodb,~gooda&goodb,~gooda&~goodb&(a==b)],
       ['both_correct','corrected','new_error','same_wrong'],default='different_wrong')

def errors():
    p=pd.read_parquet(FORMAL/'oof-predictions.parquet');folds=load('folds')
    assert len(p)==3240 and not p.duplicated(['arm','seed','session_id']).any()
    assert p.groupby(['arm','seed']).size().eq(120).all()
    expected=folds[folds.split=='test'][['session_id','fold','content_id','label_id','repetition']]
    joined=p.merge(expected,on=['session_id','fold','content_id','label_id','repetition'],validate='many_to_one')
    assert len(joined)==len(p)
    v=p[PROBS].to_numpy();assert np.isfinite(v).all() and (v>=0).all()
    np.testing.assert_allclose(v.sum(1),1,atol=2e-6)
    y=p.target.to_numpy();p['correct']=p.prediction==p.target
    p['ce_bits']=-np.log2(np.maximum(v[np.arange(len(v)),y],1e-15))
    p['brier']=((v-np.eye(6)[y])**2).sum(1)
    other=v.copy();other[np.arange(len(v)),y]=-np.inf
    p['margin']=v[np.arange(len(v)),y]-other.max(1)
    p['true_probability']=v[np.arange(len(v)),y]
    keys=['fold','seed','session_id','content_id','label_id','repetition','target']
    rows=[]
    for arm,ref in [('S2','S1'),('S2','S4'),('L3','S2')]:
        a=p[p.arm==arm];b=p[p.arm==ref]
        g=a.merge(b,on=keys,suffixes=('_arm','_ref'),validate='one_to_one')
        assert len(g)==360
        g['state']=states(g.prediction_arm,g.prediction_ref,g.target)
        g['comparison']=arm+'-'+ref
        for name in ['ce_bits','brier','margin','true_probability']:g[name+'_change']=g[name+'_arm']-g[name+'_ref']
        for seed,h in g.groupby('seed'):
            old=pd.read_parquet(FORMAL/'decision-changes.parquet').query('arm==@arm and reference==@ref and seed==@seed').iloc[0]
            assert (h.state=='corrected').sum()==old.corrected
            assert (h.state=='new_error').sum()==old.new_errors
        rows.append(g)
    ledger=save('error-ledger',pd.concat(rows,ignore_index=True))
    for level,groups in [('content',['comparison','content_id','label_id','seed']),('business',['comparison','label_id','seed'])]:
        rows=[]
        for key,g in ledger.groupby(groups):
            rows.append({**dict(zip(groups,key)),'visits':len(g),'correct_arm':int(g.correct_arm.sum()),'correct_ref':int(g.correct_ref.sum()),
              **{s:int((g.state==s).sum()) for s in ['both_correct','corrected','new_error','same_wrong','different_wrong']},
              'ce_arm':g.ce_bits_arm.mean(),'ce_ref':g.ce_bits_ref.mean(),'brier_arm':g.brier_arm.mean(),'brier_ref':g.brier_ref.mean()})
        save(level+'-errors',pd.DataFrame(rows))
    wide=p[p.arm.isin(['S1','S2','L3'])].pivot(index=keys,columns='arm',values='correct').reset_index()
    wide['A']=wide.S1&~wide.S2;wide['B']=wide.S2&~wide.L3;wide['C']=~wide.S2&~wide.L3
    assert not (wide.A&wide.B).any()
    wide['A_still_wrong_L3']=wide.A&~wide.L3;wide['B_also_wrong_S1']=wide.B&~wide.S1
    save('error-overlap-ledger',wide)
    save('youtube-details',p[p.label_id.str.startswith('youtube.com')])
    overlap=[]
    for scope,g in [('all',wide),('youtube',wide[wide.label_id.str.startswith('youtube.com')])]:
        for seed,h in g.groupby('seed'):
            overlap.append({'scope':scope,'seed':seed,'A':int(h.A.sum()),'B':int(h.B.sum()),'C':int(h.C.sum()),
             'A_L3_wrong':int(h.A_still_wrong_L3.sum()),'B_S1_wrong':int(h.B_also_wrong_S1.sum()),
             'error_union':int((~h.S2|~h.L3).sum()),'error_intersection':int(h.C.sum()),
             'A_persistent_fraction':h.A_still_wrong_L3.sum()/h.A.sum() if h.A.sum() else None})
    overlap=save('error-overlap-summary',pd.DataFrame(overlap))
    metrics=pd.read_parquet(FORMAL/'metrics-by-seed.parquet');save('metrics-by-seed',metrics)
    content=p.groupby(['arm','label_id','content_id']).agg(seed_visit_errors=('correct',lambda x:int((~x).sum())),ce_bits_sum=('ce_bits','sum')).reset_index()
    save('content-error-contribution',content)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=DOC/'figures';figdir.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(15,9),layout='constrained')
    content_order=sorted(p.content_id.unique())
    for ax,(name,g) in zip(axes,ledger.groupby('comparison')):
        x=g.assign(net=(g.state=='corrected').astype(int)-(g.state=='new_error').astype(int)).pivot_table(index='content_id',columns='seed',values='net',aggfunc='sum').reindex(content_order)
        im=ax.imshow(x,vmin=-4,vmax=4,cmap='RdBu');ax.set_title(name+' corrected - new errors');ax.set_xticks(range(3),['seed18','seed19','seed20']);ax.set_yticks(range(30),range(1,31))
    fig.colorbar(im,ax=axes,label='Visits per content (out of 4)');fig.savefig(figdir/'content-changes.png',dpi=150);plt.close(fig)
    save('figure-content-index',pd.DataFrame({'row':range(1,31),'content_id':content_order}))
    txt='# 记录表示与配对预训练：现有预测定位\n\n旧模型未重训。120访问、30内容；跨seed计数不增加独立样本量。\n\n## 三seed完整指标\n\n'+table(metrics[metrics.arm.isin(['S1','S2','S4','L3'])])
    txt+='\n\n## 错误交集（每seed独立列出）\n\nA=S1正确且S2错误；B=S2正确且L3错误；C=S2和L3均错误。A与B天然互斥。\n\n'+table(overlap)
    txt+='\n\n## YouTube全部内容的错误及CE贡献\n\n计数为seed×visit，单内容分母12，不是12独立访问。\n\n'+table(content[content.arm.isin(['S1','S2','S4','L3'])&content.label_id.str.startswith('youtube.com')])
    txt+='\n\n![逐内容净修复](figures/content-changes.png)\n\n行号与内容映射见figure-content-index.parquet；完整错误及概率变化见error-ledger.parquet。新增定位为探索性描述，不用于删除样本或选择超参数。旧配对区间沿用原报告，不把区间跨零当等效。\n'
    (DOC/'error-localization.md').write_text(txt,encoding='utf-8')
    print('Error localization complete',flush=True)

def encoder_hash(model):
    h=hashlib.sha256()
    for n,p in model.state_dict().items():
        if n.startswith(ENCODER):h.update(n.encode());h.update(p.detach().cpu().numpy().tobytes())
    return h.hexdigest()

def extract(model,view,ids,state,device):
    chunks=[]
    with torch.no_grad():
        for start in range(0,len(ids),6):
            batch=ids[start:start+6];x,sizes=input_visits(view,batch,'S2',state,device)
            h=model.flows(x,'S2');rows=[];offset=0
            for size in sizes:
                a=h[offset:offset+size];offset+=size
                rows.append(torch.cat([a.mean(0),a.max(0).values,a.new_tensor([np.log1p(size)])]))
            z=torch.stack(rows)
            torch.testing.assert_close(model.head(z),model.visits(x,sizes,'S2'),atol=2e-5,rtol=2e-4)
            chunks.append(z)
    return torch.cat(chunks)

def probes():
    store=Store();folds=load('folds');scalers=read(OLD/'preprocessors.json');labels=sorted(load('cohort').label_id.unique())
    done_count=0
    for fold in range(5):
      tr=folds[(folds.fold==fold)&(folds.split=='train')];te=folds[(folds.fold==fold)&(folds.split=='test')]
      assert len(tr)==96 and len(te)==24 and not set(tr.content_id)&set(te.content_id)
      state={r:scalers[f'{fold}:{r}'] for r in ['P','R','C','T']}
      assert all(set(s['fit_visits'])==set(tr.session_id) for s in state.values())
      for seed in cfg()['seeds']:
       for source in range(5):
        name=f'f{fold}-s{seed}-Q{source}';folder=OUT/name;folder.mkdir(exist_ok=True)
        if (folder/'done.json').exists():
            old=read(folder/'done.json');assert old['contract']==digest(OUT/'contract.json')
            assert digest(folder/'predictions.parquet')==old['predictions_sha256'];done_count+=1;continue
        device=setup(seed);model=Hierarchy().to(device)
        # Fresh head is exactly shared across sources by reinitializing before loading encoder.
        initial_head={n:p.detach().clone() for n,p in model.head.named_parameters()}
        if source:
            path=FORMAL/f'f{fold}-s{seed}-L{source}-ssl/final.pt'
            source_state=torch.load(path,map_location=device,weights_only=False)['model']
            fresh=model.state_dict()
            for n in fresh:
                if n.startswith(ENCODER):fresh[n]=source_state[n]
            model.load_state_dict(fresh)
        for p in model.parameters():p.requires_grad_(False)
        model.eval();before=encoder_hash(model);started=time.perf_counter()
        train_view=View(store,tr.session_id,['post']);test_view=View(store,te.session_id,['post'])
        assert not set(train_view.uid_to_visit)&set(test_view.uid_to_visit)
        assert all(side=='post' for _,side in test_view.data)
        x=extract(model,train_view,tr.session_id.tolist(),state,device)
        xt=extract(model,test_view,te.session_id.tolist(),state,device)
        assert x.is_cuda and xt.is_cuda and x.shape==(96,65) and xt.shape==(24,65)
        np.savez_compressed(folder/'embeddings.npz',train=x.cpu().numpy(),test=xt.cpu().numpy(),train_ids=tr.session_id.to_numpy(dtype=str),test_ids=te.session_id.to_numpy(dtype=str))
        for p in model.head.parameters():p.requires_grad_(True)
        head=model.head;head.train();opt=torch.optim.Adam(head.parameters(),lr=.001)
        y=torch.tensor([labels.index(v) for v in tr.label_id],device=device)
        index={s:i for i,s in enumerate(tr.session_id)}
        schedule=read(OLD/f'schedule-{fold}-{seed}.json')
        batches=torch.tensor([[index[b['session_id']] for b in slot['batch']] for slot in schedule],device=device)
        assert batches.shape==(1000,24);history=[]
        for step,ix in enumerate(batches):
            opt.zero_grad(set_to_none=True);ce=torch.nn.functional.cross_entropy(head(x[ix]),y[ix])
            loss=ce+.5*1e-4*sum(p.square().sum() for n,p in head.named_parameters() if n.endswith('weight'))
            assert torch.isfinite(loss);loss.backward();opt.step()
            history.append({'step':step+1,'loss':float(loss.detach()),'ce_nats':float(ce.detach())})
        assert before==encoder_hash(model)
        assert all(p.grad is None for n,p in model.named_parameters() if n.startswith(ENCODER))
        assert any(not torch.equal(p,initial_head[n]) for n,p in head.named_parameters())
        head.eval()
        with torch.no_grad():prob=torch.softmax(head(xt),1)
        assert prob.is_cuda and torch.isfinite(prob).all()
        values=prob.cpu().numpy();rows=[]
        for r,v in zip(te.to_dict('records'),values):
            rows.append({**r,'arm':f'Q{source}','seed':seed,'target':labels.index(r['label_id']),'prediction':int(v.argmax()),**dict(zip(PROBS,v.tolist()))})
        pd.DataFrame(rows).to_parquet(folder/'predictions.parquet',index=False)
        pd.DataFrame(history).to_parquet(folder/'training-log.parquet',index=False)
        torch.save({'head':head.state_dict(),'encoder_hash':before,'contract':digest(OUT/'contract.json')},folder/'head.pt')
        torch.cuda.synchronize()
        write_json(folder/'done.json',{'contract':digest(OUT/'contract.json'),'encoder_unchanged':True,'encoder_hash':before,'cuda':True,'test_pre':False,'steps':1000,'seconds':time.perf_counter()-started,
          'embedding_std_mean':float(x.std(0).mean()),'predictions_sha256':digest(folder/'predictions.parquet')})
        done_count+=1;write_json(OUT/'progress.json',{'completed':done_count,'total':75,'last':name,'status':'running'})
        print(name,done_count,'/75',flush=True)
        del model,head,opt,train_view,test_view,x,xt;torch.cuda.empty_cache()
    write_json(OUT/'progress.json',{'completed':75,'total':75,'status':'complete'})

def report():
    frames=[pd.read_parquet(p) for p in OUT.glob('f*-Q*/predictions.parquet')]
    assert len(frames)==75
    p=save('probe-oof',pd.concat(frames,ignore_index=True));assert len(p)==1800
    cohort=load('cohort').sort_values('session_id');ids=cohort.session_id.tolist();target=None;arrays={};metrics=[]
    for (arm,seed),g in p.groupby(['arm','seed']):
        g=g.set_index('session_id').loc[ids];v=g[PROBS].to_numpy();target=g.target.to_numpy();arrays[arm,seed]=v
        metrics.append({'arm':arm,'seed':seed,**dict(zip(NAMES,scores(target,v)))})
    metrics=save('probe-metrics',pd.DataFrame(metrics));avg=metrics.groupby('arm')[NAMES].mean()
    contrasts=[('Q3','Q0'),('Q3','Q1'),('Q3','Q2'),('Q3','Q4'),('Q1','Q0'),('Q2','Q0'),('Q4','Q0')]
    groups=[cohort[cohort.label_id==label].content_id.unique().tolist() for label in sorted(cohort.label_id.unique())]
    rng=np.random.default_rng(20260926);draws=[]
    # Old artifact stores metric draws, not sampled content IDs. Reconstruct the exact RNG recipe.
    for draw in range(2000):
        selected=[c for group in groups for c in rng.choice(group,len(group),replace=True)]
        weights=np.array([selected.count(c) for c in cohort.content_id]);assert weights.sum()==120
        result={a:np.mean([scores(target,arrays[a,s],weights) for s in cfg()['seeds']],axis=0) for a in avg.index}
        for a,b in contrasts:draws.append({'draw':draw,'arm':a,'reference':b,**dict(zip(NAMES,(result[a]-result[b])*[1,1,-1,-1]))})
    draws=save('probe-bootstrap',pd.DataFrame(draws));gains=[]
    for a,b in contrasts:
        d=draws[(draws.arm==a)&(draws.reference==b)];row={'arm':a,'reference':b}
        for metric,sign in zip(NAMES,[1,1,-1,-1]):
            row[metric+'_gain']=sign*(avg.loc[a,metric]-avg.loc[b,metric]);row[metric+'_low']=d[metric].quantile(.025);row[metric+'_high']=d[metric].quantile(.975)
        gains.append(row)
    gains=save('probe-gains',pd.DataFrame(gains))
    recalls=p.groupby(['arm','seed','label_id']).apply(lambda g:float((g.prediction==g.target).mean()),include_groups=False).rename('recall').reset_index();save('probe-recall',recalls)
    txt='# 冻结flow表示探针\n\n75/75任务完成；只训练原65→32→6小型非线性头，编码器逐任务验证未改变。训练、编码、测试均CUDA。Q0随机编码器；Q1–Q4为L1–L4的SSL结束编码器。\n\n## 三seed均值\n\n'+table(avg.reset_index())+'\n\n## 逐seed\n\n'+table(metrics)
    txt+='\n\n## 固定对照\n\n正值均表示改善。区间条件于固定模型，内容级分层bootstrap，未作多重比较校正；跨零不是等效。\n\n'+table(gains)
    txt+='\n\n本轮只解释固定低容量头下的业务可读性，不估计互信息，也不证明微调造成某种语义破坏。不同编码器输出尺度与固定正则可能影响读出，故不是表示信息量绝对排名。S2是端到端监督参照，不是冻结探针对照。范围仍限已见VLESS与离线索引关联队列。\n'
    (DOC/'frozen-probe-results.md').write_text(txt,encoding='utf-8')
    write_json(OUT/'completion.json',{'tasks':75,'OOF_rows':1800,'device':'cuda','contract':digest(OUT/'contract.json')})
    print(avg.to_string(),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['errors','probe','report','all'],default='all');args=parser.parse_args()
    freeze()
    if args.stage in ['errors','all']:errors()
    if args.stage in ['probe','all']:probes()
    if args.stage in ['report','all']:report()
