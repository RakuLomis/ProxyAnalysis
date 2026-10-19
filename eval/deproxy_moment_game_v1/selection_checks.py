"""CPU score-only synthetic ties and six-class confusion arithmetic, no real query."""
from common import *
from formal import choose,metrics

def run():
    vals=[dict(candidate=r['id'],gamma=r['gamma'],lr=r['lr'],beta=b,F1_U=.6,CE_U=.5) for r in RECIPES for b in BETAS]
    require(choose(vals,'FUSE')['candidate']=='H03' and choose(vals,'FUSE')['beta']==0,'FUSE frozen tie order')
    require(choose([x for x in vals if x['beta']==1],'PURE')['candidate']=='H03','PURE fixed gamma/lr tie order')
    changed=[dict(x) for x in vals];changed[0]['F1_U']+=.5e-12
    require(choose(changed,'FUSE')['candidate']=='H03','F1 tolerance changed')
    changed[0]['F1_U']+=1e-8
    require(choose(changed,'FUSE')['candidate']=='H01','F1 does not precede regularization')
    changed=[dict(x) for x in vals];changed[0]['CE_U']-=1e-8
    require(choose(changed,'FUSE')['candidate']=='H01','CE does not precede regularization')
    y=np.repeat(np.arange(6),4);z=y.copy();z[[2,7,12,18]]=[4,0,0,1]
    p=np.full((24,6),.01);p[np.arange(24),z]=.95;lp=np.log(p)
    m,cm,f=metrics(y,lp,[0,1]);manual=[]
    for k in range(6):manual.append(2*np.sum((y==k)&(z==k))/(np.sum(y==k)+np.sum(z==k)))
    require(np.max(abs(np.array(manual)-f))<1e-14 and abs(m['F1_U']-np.mean(manual[:2]))<1e-14,'Six-class F1_U, not U-only binary matrix')
    require(abs(m['CE']+lp[np.arange(24),y].mean())<1e-14,'CE log-probability arithmetic')
    immutable(OUT/'tests/P1-selection-math.json',dict(passed=True,checks=7,real_query_reads=0,H_U_reads=0,selection_uses_full_six_class_matrix=True,
        selection_tie=1e-12,score_only_CPU=True))

if __name__=='__main__':run()
