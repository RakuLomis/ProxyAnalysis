"""Approved diagnostic-only repair, original preservation and pre-resume seal."""
import ast
import copy
import shutil
import sys
from common import *

REV=OUT/'manifests/engineering-repair-v1'
def snapshot():
    c=start('repair-snapshot'); require(not (REV/'preservation.json').exists(),'Repair snapshot already sealed')
    require(not list((OUT/'models').rglob('DSR*-a*.pt')),'No candidates may precede diagnostic repair')
    require(not (OUT/'selection').exists() and not (OUT/'predictions').exists(),'No outcomes before repair')
    (REV/'original-source').mkdir(parents=True,exist_ok=True)
    for p,h in c['source_sha256'].items():
        dst=REV/'original-source'/Path(p).name; shutil.copy2(ROOT/p,dst); require(sha(dst)==h,'Original snapshot mismatch')
    shutil.copy2(OUT/'manifests/experiment-contract.json',REV/'original-contract.json')
    preserved={}
    for directory in ['kernels','models','states','packages','CF-predictions']:
        for p in (OUT/directory).rglob('*'):
            if p.is_file(): preserved[rel(p)]=sha(p)
    write(REV/'preservation.json',{'created_unix':time.time(),'original_contract_sha256':sha(REV/'original-contract.json'),
       'source_sha256':c['source_sha256'],'preserved_artifacts':preserved,'positive_fits':0,'approved_date':'2026-10-06'})
    print('Original contract/source preserved; artifacts:',len(preserved),flush=True)

def body(p,name):
    tree=ast.parse(Path(p).read_text(encoding='utf-8'))
    return ast.dump(next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name),include_attributes=False)

def seal():
    configure(); require(not (OUT/'manifests/experiment-contract-amended-v1.json').exists(),'Amendment exists')
    preserve=read(REV/'preservation.json'); original=read(REV/'original-contract.json')
    require(sha(OUT/'manifests/experiment-contract.json')==preserve['original_contract_sha256'],'Original contract changed')
    for p,h in preserve['preserved_artifacts'].items(): require(sha(ROOT/p)==h,'Existing source/state changed')
    for p,h in original['baseline_sha256'].items(): require(sha(ROOT/p)==h,'Baseline changed')
    for p,h in original['packages_sha256'].items(): require(sha(ROOT/p)==h,'Package changed')
    src=Path(__file__).parent
    for name in ['objective','optimize','risks','partition','probabilities','standardize']:
        require(body(src/'common.py',name)==body(REV/'original-source/common.py',name),'Mathematical implementation changed')
    require(body(src/'train.py','main')==body(REV/'original-source/train.py','main'),'Training matrix changed')
    from train import activity
    logs=[]
    y=tensor(np.repeat(np.arange(6),4),torch.long); gamma,_=partition(tensor(np.tile([1,2,2,3],6)),y)
    x=tensor(np.arange(24*96).reshape(24,96)%13/13)
    model={'weight':tensor(np.arange(6*96).reshape(6,96)%7/100),'bias':tensor(np.arange(6)/100)}
    for case,m,ref in [('baseline',model,model),('nonzero_delta',{'weight':model['weight']+.003,'bias':model['bias']+tensor([.01,-.01,.02,-.02,0,0])},model)]:
        parts,grads=activity(m,x,y,gamma,ref)
        w=m['weight'].clone().requires_grad_(); b=m['bias'].clone().requires_grad_()
        _,p=objective(w,b,x,y,gamma,ref['weight'],ref['bias'],.5)
        expected=.001*torch.sqrt(w.square().sum())
        require(abs(grads['L2_gradient_norm']-float(expected))<1e-12,'L2 gradient norm')
        require(grads['L2_bias_gradient_norm']==0.,'L2 bias must be explicitly zero')
        strict={}
        for n,t in [('CE',p['CE']),('drift',p['drift_gap']),('protection',ETA*p['stay'])]:
            gw,gb=torch.autograd.grad(t,[w,b],retain_graph=True)
            require(gw is not None and gb is not None,'Unexpected unused gradient')
            strict[n]=float(torch.sqrt(gw.square().sum()+gb.square().sum()))
            require(abs(grads[n+'_gradient_norm']-strict[n])<1e-12,'Diagnostic changed gradient')
        logs.append({'case':case,'passed':True,'L2_bias_gradient_norm':0.,'L2_expected_norm':float(expected),'other_gradients_strict':True})
    # Actual first failed role: only a gradient read, no optimizer or validation.
    r=next(r for r in original['roles'] if r['inner'] is not None)
    h=pd.read_parquet(mainfolder('packages',r)/'train-post.parquet')
    base=torch.load(oldfolder('models',r)/'zero.pt',map_location=device(),weights_only=True)
    g=torch.load(mainfolder('states',r)/'DSR2.pt',map_location=device(),weights_only=True)
    p,grads=activity(base,(tensor(h[HIST])-base['mu'])/base['scale'],tensor(truths(h),torch.long),g['gamma'])
    require(grads['L2_bias_gradient_norm']==0. and all(np.isfinite(v) for v in grads.values()),'Actual-role gradient diagnostic')
    logs.append({'case':rolekey(r),'passed':True,'gradients':grads})
    write(REV/'repair-tests.json',logs)
    amended=copy.deepcopy(original)
    changed={p:sha(ROOT/p) for p in original['source_sha256'] if sha(ROOT/p)!=original['source_sha256'][p]}
    require(set(Path(p).name for p in changed)=={'common.py','train.py','report.py','README.md'},'Unexpected repaired files')
    amended['source_sha256'].update(changed); amended['source_sha256'][rel(Path(__file__))]=sha(__file__)
    amended['engineering_revision']={'version':1,'sealed_unix':time.time(),'approved_date':'2026-10-06',
       'reason':'L2 diagnostic has mathematically zero bias derivative; no bias regularization added',
       'original_contract_sha256':preserve['original_contract_sha256'],'changed_files':changed,
       'objective_AST_unchanged':True,'train_matrix_AST_unchanged':True,'resume_at':'D14',
       'outcomes_opened':False,'existing_CF_states_unchanged':True}
    write(OUT/'manifests/experiment-contract-amended-v1.json',amended)
    write(REV/'amendment-seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract-amended-v1.json'),
      'tests_sha256':sha(REV/'repair-tests.json'),'source_sha256':amended['source_sha256'],'sealed_unix':time.time()})
    print('Diagnostic-only amendment sealed; unchanged mathematical targets and existing artifacts',flush=True)

if __name__=='__main__': {'snapshot':snapshot,'seal':seal}[sys.argv[1]]()
