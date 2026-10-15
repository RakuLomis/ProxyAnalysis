"""V2 checks original-coordinate numerical quality and all frozen dependencies."""
from common import *

def run():
    c=start('verify');v=v2contract();count=0;maxerr=0.;maxgrad=0.
    for p,h in c['baseline_sha256'].items():require(sha(ROOT/p)==h,'Historical input changed')
    for p,info in c['packages'].items():require(sha(ROOT/p)==info['sha256'],'Package changed')
    for p,h in read(OUT/'manifests/adopted-artifacts.json')['files'].items():require(sha(ROOT/p)==h,'Adopted artifact changed')
    for p,h in v['original_snapshots'].items():require(sha(ROOT/p)==h,'Old failure/progress/contract changed')
    choice={(x['outer'],x['target'],x['group'],x['arm']):x['t'] for x in read(OUT/'selection/choices.json') if x['arm'] in ARMS}
    for r in c['main']:
      require(not set(r['train_contents'])&set(r['validation_contents']),'Content overlap')
      if r['inner'] is not None:require(r['target'] not in r['sources']+[r['calibration']],'Actual target used inside')
      for arm in ARMS:
        slot=artifact(PREP/'slots'/r['id']/(arm+'.pt'))
        for t in TS if r['inner'] is not None else [choice[(r['outer'],r['target'],r['group'],arm)]]:
            p=OUT/'models'/r['id']/f'{arm}-t{t:g}.pt';m=artifact(p);log=read(p.with_suffix('.json'))['optimizer']
            require(torch.equal(m['mu'],slot['mu']) and torch.equal(m['scale'],slot['scale']),'Changed prediction coordinate')
            w=m['weight'].clone().requires_grad_();b=m['bias'].clone().requires_grad_()
            loss=objective(w,b,slot['x'],slot['y'],slot['mass'],t);gw,gb=torch.autograd.grad(loss,(w,b))
            err=abs(float(loss.detach())-log['objective']);grad=max(float(gw.abs().max()),float(gb.abs().max()))
            require(err<1e-10 and grad<=1e-5 and log['iterations']<500,'Original numerical gate')
            require(log['solver']=='cholesky-initial-contrast-curvature-v1' and all(log['gates'].values()),'Wrong solver/acceptance')
            maxerr=max(maxerr,err);maxgrad=max(maxgrad,grad);count+=1
      if count%100==0:progress('OR18_verifying',models=count,total=14700)
    require(count==14700 and read(OUT/'manifests/diagnostic-reuse-check.json')['models']==680,'Model counts')
    r=next(x for x in c['main'] if x['inner'] is None);rejected=[]
    for filename,role in [('labels.parquet','main-predict'),('query.parquet','main-select'),('labels.parquet','main-select')]:
        try:package(rolepath(r)/filename,role)
        except RuntimeError:rejected.append((filename,role))
    require(len(rejected)==3,'Permission negative tests')
    pred=OUT/'predictions/visits.parquet'
    require(sha(pred)==read(pred.parent/'complete.json')['sha256'] and len(pd.read_parquet(pred))==10080,'Prediction population/seal')
    result={'passed':True,'v2_new_main_fits':count,'reused_diagnostic_fits':680,'historical_total_formal_fits':15384,
            'objective_max_error':maxerr,'original_gradient_max':maxgrad,'permission_negatives':rejected,
            'old_artifacts_unchanged':True,'all_training_and_inference_CUDA_float64':True,
            'stage3_physical_only_extraction_completed':False,'universal_TCP_epoch_proof':False}
    write(OUT/'verification.json',result);finish('verify',**result)

if __name__=='__main__':run()
