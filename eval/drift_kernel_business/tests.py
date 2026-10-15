"""Artificial tests only; never uses real test labels to develop methods."""
from common import *

def run():
    checks=[]
    def check(value,name):
        require(value,name)
        checks.append(name)
    a=tensor([[.8,.2],[.3,.7]])
    k=tensor([[.9,.1],[.2,.8]])
    check(torch.allclose(a@k,tensor([[.76,.24],[.41,.59]])), 'hand computed orientation')
    check(torch.allclose(a@torch.eye(2,device=cuda(),dtype=torch.float64),a),'identity kernel')
    check(torch.allclose((a[0].expand(6,-1)@k)[0],(a[0].expand(6,-1)@k)[5]),'equal source classes')
    check(torch.allclose(a@tensor([[.4,.6],[.4,.6]]),tensor([[.4,.6],[.4,.6]])),'constant rows remove class information')
    for f in FEATURES:
        edge=BYTE_EDGES if size(f)==9 else COUNT_EDGES
        check(np.array_equal(encode([0,*edge],f),np.arange(size(f))), 'fixed edges '+f)
    rows=pd.DataFrame({'session_id':['a','a','b'],'content_id':['x','x','y'],
                      **{'post_'+f:[0,1,2] for f in FEATURES}})
    ids,h=visits_histogram(rows,'post')
    _,dup=visits_histogram(pd.concat([rows,rows],ignore_index=True),'post')
    check(torch.allclose(h,dup,atol=1e-12),'histogram replication invariant')
    check(np.allclose(rows.assign(w=mass(rows)).groupby('content_id').w.sum(),1),'content mass invariant')
    replicated=pd.concat([rows,rows],ignore_index=True)
    check(np.allclose(replicated.assign(w=mass(replicated)).groupby('content_id').w.sum(),1),'replicated flow mass invariant')
    tables={f:torch.full((6,size(f)),1/size(f),dtype=torch.float64,device=cuda()) for f in FEATURES}
    s=composite(h,tables)
    check(torch.allclose(s.softmax(1),torch.full_like(s,1/6),atol=1e-12),'uniform posterior and natural logs')
    joint=tensor([[1.,2.],[3.,4.]])
    check(torch.allclose((joint.sum(1)/joint.sum())@(joint/joint.sum(1)[:,None]),joint.sum(0)/joint.sum()), 'class conditional marginalization identity')
    check(len(HIST)==96 and abs(sum(WEIGHTS)-1)<1e-12,'coordinates and family weights')
    write(OUT/'manifests/unit-tests.json',{'passed':True,'checks':checks,'device':'cuda:0',
            'real_test_predictions_generated':False})
    print('Artificial checks passed:',len(checks),flush=True)

if __name__=='__main__':
    run()
