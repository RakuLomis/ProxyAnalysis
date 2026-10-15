"""Synthetic tests precede real direction/weight construction and registration."""
from common import *
def main():
    configure(); rows=[]
    def ck(name,ok): require(ok,name); rows.append({'test':name,'pass':True})
    y=tensor(np.repeat(np.arange(6),4),torch.long); d=tensor(np.tile([1.,2.,2.,3.],6)); g=partition(d,y)
    ck('fractional median ties',torch.equal(g[:4,0],tensor([1,.5,.5,0])))
    hard,risk=direction(d,y,g); ck('high OOF CE hard direction',hard==1)
    ck('low direction accepted',direction(-d,y,g)[0]==0)
    ck('exact and numerical ties have null direction',direction(torch.ones_like(d),y,g)[0] is None and direction(d*1e-14,y,g)[0] is None)
    torch.manual_seed(20261006); x=torch.randn(24,96,device=device(),dtype=torch.float64)/10
    W=torch.randn(6,96,device=device(),dtype=torch.float64)/20; b=torch.zeros(6,device=device(),dtype=torch.float64)
    base={'weight':W,'bias':b}; ce=F.cross_entropy(x@W.T+b,y,reduction='none'); rr=risks(ce,y,g)
    for r in RATIOS:
        w=weights(g,hard,r)
        ck(f'r{r} positive bounds and mean',float(w.min())>=.4-1e-12 and float(w.max())<=1.6+1e-12 and abs(float(w.mean())-1)<1e-12)
        ck(f'r{r} each-class mean',all(abs(float(w[y==j].mean())-1)<1e-12 for j in range(6)))
        ck(f'r{r} weighted risk identity',abs(float((ce*w).mean()-(rr[0]+r*rr[1])/(1+r)))<1e-12)
        ck(f'r{r} null alias',torch.equal(weights(g,None,r),torch.ones_like(d)))
        ck(f'r{r} whole-soft alias',torch.equal(weights(torch.full_like(g,.5),1,r),torch.ones_like(d)))
    w=weights(g,1,2.); val,parts=objective(W,b,x,y,w,g,base)
    ck('zero ratio exact base target',abs(float(objective(W,b,x,y,weights(g,1,1),g,base)[0]-(ce.mean()+.0005*W.square().sum())))<1e-12)
    ck('base protection zero',float(parts['stay'])==0)
    ck('uniform class-score shift invariant',float(objective(W,b+3,x,y,w,g,base)[1]['stay'])<1e-28)
    wt=W.clone().requires_grad_(); bt=b.clone().requires_grad_(); loss,_=objective(wt,bt,x,y,w,g,base)
    grad=torch.autograd.grad(loss,wt)[0][0,0]; e=1e-5; p=W.clone(); m=W.clone(); p[0,0]+=e; m[0,0]-=e
    fd=(objective(p,b,x,y,w,g,base)[0]-objective(m,b,x,y,w,g,base)[0])/(2*e)
    ck('finite difference gradient',abs(float(grad-fd))<1e-8)
    ck('fixed-weight convex Jensen',float(objective(W*.8,b,x,y,w,g,base)[0])<=float((objective(W*.6,b,x,y,w,g,base)[0]+objective(W,b,x,y,w,g,base)[0])/2)+1e-12)
    ck('L2 bias explicit zero and strict other gradients',gradients(W,b,x,y,w,g,base)['L2_bias_gradient_norm']==0)
    bad=pd.DataFrame({'visit_id':['x'],**{k:[0.] for k in HIST},'content_id':['forbidden']})
    caught=False
    try: validate_query(bad)
    except RuntimeError: caught=True
    ck('inference rejects content/pre/label extra columns',caught)
    caught=False
    try: validate_gamma(torch.zeros_like(g),y)
    except RuntimeError: caught=True
    ck('invalid gamma rejected',caught)
    for name,src,query,parent in [('overlap',['a'],['a'],['a']),('wrong parent',['a','c'],['b'],['a','b'])]:
        caught=False
        try: validate_scope(src,query,parent)
        except RuntimeError: caught=True
        ck('CF rejects '+name,caught)
    validate_scope(['a'],['b'],['a','b']); ck('CF correct scope accepted',True)
    ck('empty optimizer schema complete',list(pd.DataFrame([],columns=OPT_COLUMNS))==OPT_COLUMNS)
    write(OUT/'manifests/unit-tests.json',rows); print('synthetic CUDA tests',len(rows),flush=True)
if __name__=='__main__': main()
