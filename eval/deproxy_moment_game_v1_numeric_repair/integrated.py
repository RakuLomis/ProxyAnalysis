"""One uniform NER1 fixed P1, all fresh heads; no automatic outer experiment."""
from common import *
from classifier import basis
from problems import load,initial_arrays,initial_head,arrays
from simplex import project_blocks,valid
from throughput import concurrent
from replay import BoundEngine,bind
from models import generate

def run(cap,phase):
    configure(cap);tag=f'R4-{phase}-{cap}';begin(tag);rows=[]
    try:
        workers=read(OUT/'tests/backend-choice.json')['workers']
        def fit_batch(problems):
            for i in range(0,len(problems),32):
                result=concurrent(problems[i:i+32],workers,OUT/'integrated/unused')
                for p in problems[i:i+32]:
                    q=result[p['spec']['key']]
                    rows.append(dict(**p['spec'],iterations=q['iterations'],evaluations=q['evaluations'],seconds=q['seconds'],
                        objective=q['objective'],original_gradient_max=q['original_gradient_max'],accepted=q['accepted'],
                        output_path=rel(p['output_path']),rows=len(p['x'])))
        if phase=='initial':
            require(cap in ['G','E'],'Initial process capability')
            side='pre' if cap=='G' else 'post';problems=[]
            for r in roles():
                x,y,w=initial_arrays(r,side)
                for g in GAMMAS:
                    s=dict(key=f'{r["id"]}/{side}/g{g:g}',role_id=r['id'],arm=side,kind='initial',gamma=g,capability=side)
                    problems.append(dict(x=x,y=y,w=w,gamma=g,init=None,spec=s,
                        output_path=OUT/'integrated/initial'/r['id']/side/f'g{g:g}.pt'))
            fit_batch(problems)
        elif phase=='static':
            require(cap in ['P','G'],'Static process capability');problems=[];arm='R-'+cap
            for r in roles():
                d=load(r,arm);x,y,w=arrays(d,project_blocks(d['anchor']))
                for g in GAMMAS:
                    s=dict(key=f'{r["id"]}/{arm}/g{g:g}',role_id=r['id'],arm=arm,kind='static',gamma=g,capability=cap)
                    problems.append(dict(x=x,y=y,w=w,gamma=g,init=initial_head(r,'pre',g,True),spec=s,
                        output_path=OUT/'integrated/models'/r['id']/arm/f'g{g:g}'/'head.pt'))
            fit_batch(problems)
        elif phase=='dynamic':
            jobs=[j for j in registration()['jobs'] if capfor(j['arm'])==cap]
            for lr in [.0003,.001]:
                batch=sorted([j for j in jobs if j['recipe']['lr']==lr],key=lambda j:(j['role_id'],j['arm'],j['recipe']['id'],j['seed']))
                ds=[];hs=[];cache={}
                for j in batch:
                    r=lookup(j['role_id']);key=(r['id'],j['arm'])
                    if key not in cache:cache[key]=load(r,j['arm'])
                    h=initial_head(r,'post' if cap=='E' else 'pre',j['recipe']['gamma'],True)
                    d,h=bind(cache[key],j,h);ds.append(d);hs.append(h)
                engine=BoundEngine(ds,batch,hs,True);engine.capture();traces=[[] for _ in batch]
                for stop in [0,1,100,500,1000,2000]:
                    deadline();engine.advance(stop-engine.steps);ck=engine.checkpoint();logs=engine.diagnostics()
                    for i,j in enumerate(batch):
                        p=OUT/'integrated/models'/j['role_id']/j['arm']/j['recipe']['id']
                        put(p/f'step-{stop:04}.pt',dict(parameters=ck['parameters'][i],adam=ck['adam'][i],gradients=ck['gradients'][i],steps=stop,clips=ck['clips'][i]),
                            role_id=j['role_id'],capability=cap)
                        traces[i].append(logs[i])
                    progress('R4_Adam',capability=cap,lr=lr,step=stop,models=len(batch))
                problems=[];q=basis()
                for i,(j,d) in enumerate(zip(batch,ds)):
                    p=OUT/'integrated/models'/j['role_id']/j['arm']/j['recipe']['id'];st=ck['parameters'][i]
                    with torch.no_grad():hat,_=generate(st,d);valid(hat)
                    x,y,w=arrays(d,hat)
                    s=dict(key=f'{j["role_id"]}/{j["arm"]}/{j["recipe"]["id"]}',role_id=j['role_id'],arm=j['arm'],kind='refit',gamma=j['recipe']['gamma'],capability=cap)
                    problems.append(dict(x=x,y=y,w=w,gamma=s['gamma'],init=dict(W=q@st['A'],c=q@st['c']),spec=s,output_path=p/'head.pt'))
                    write(p/'trace.json',dict(steps=traces[i],uniform_lr_bucket=True,bucket_lr=lr,bucket_models=len(batch),numeric_version='NER1'),True)
                del engine;fit_batch(problems);torch.cuda.empty_cache()
        else:raise RuntimeError('Unknown fixed P1 phase')
        save(OUT/'tests'/f'{tag}.parquet',rows)
        write(OUT/'tests'/f'{tag}.json',dict(passed=True,heads=len(rows),query_read=False),True);codecheck()
    except BaseException as e:
        if rows:save(OUT/'tests'/f'{tag}-partial.parquet',rows)
        failure(tag,e);raise
    finally:end(tag)

def export(cap):
    configure(cap);begin('R4-export-'+cap);records=[]
    try:
        for r in roles():
            arms=['E-post'] if cap=='E' else (['R-G','F-G'] if cap=='G' else ['R-P','N-P','F-P'])
            for arm in arms:
                d=load(r,arm)
                for p in sorted((OUT/'integrated/models'/r['id']/arm).glob('*/head.pt')):
                    head=newown(p,r['id']);statepath=p.parent/'step-2000.pt'
                    st=newown(statepath,r['id'])['parameters'] if statepath.exists() else None
                    anchor=None if cap=='E' else own(OLD/'anchors'/r['id']/f'{cap}.pt',r['id'])
                    value=dict(head=head,mu_A=d['mu_A'],scale_A=d['scale_A'],mu_B=d['mu_B'],scale_B=d['scale_B'],
                        anchor=anchor,residual=None if st is None else {k:st[k] for k in ['U1','d1','U2']})
                    put(p.parent/'export.pt',value,role_id=r['id'],capability=cap,post_only_interface=True)
                    # Independent deployed path accepts raw training post only.
                    b=d['b'];z=(b-value['mu_B'])/value['scale_B']
                    from ridge_anchor import forward
                    a=b if anchor is None else forward(z,anchor)
                    if st is not None:a=a+F.linear(F.relu(F.linear(z,st['U1'],st['d1'])),st['U2'])
                    a=project_blocks(a);valid(a)
                    pred=F.linear((a-value['mu_A'])/value['scale_A'],head['W'],head['c'])
                    with torch.no_grad():reference=generate(st,d)[0] if st is not None else project_blocks(d['anchor'])
                    truth=((reference-d['mu_A'])/d['scale_A'])@head['W'].T+head['c']
                    err=float((pred.log_softmax(1)-truth.log_softmax(1)).abs().max())
                    require(err<=1e-10,'Post-only export replay')
                    records.append(dict(role_id=r['id'],arm=arm,candidate=p.parent.name,log_probability_error=err,rows=len(b)))
        save(OUT/'tests'/f'R4-export-{cap}.parquet',records)
        write(OUT/'tests'/f'R4-export-{cap}.json',dict(passed=True,exports=len(records),query_read=False),True);codecheck()
    except BaseException as e:failure('R4-export-'+cap,e);raise
    finally:end('R4-export-'+cap)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['initial','static','dynamic','export']);p.add_argument('--cap',choices=['P','G','E'],required=True)
    a=p.parse_args();export(a.cap) if a.phase=='export' else run(a.cap,a.phase)
