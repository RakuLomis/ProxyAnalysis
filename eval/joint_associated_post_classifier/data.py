"""Train-only packages; preserve original classification slots and real-post order."""
from common import *

def pilot_roles():
    order={p:PROTOCOLS[(i+1)%4] for i,p in enumerate(PROTOCOLS)}
    return [r for r in contract()['inner_roles'] if r['outer']==0 and r['inner']==1 and r['calibration']==order[r['target']]]

class TrainingPool:
    def __init__(self):self.cache={}
    def get(self,r,arm='JC',lam=0.):
        inner=r['inner'] is not None
        if not inner:
            from workflow import authorized
            authorized()
        rid=r['id'];key=(rid,'common')
        if key not in self.cache:
            s=asset(PARENT/'packages'/rid/'classification.pt',rid,'classification')
            b=asset(PARENT/'base-models'/rid/'P-small.pt',rid,'base')
            require(set(s)=={'x','y','mass','real_x','real_mass','mu','scale'},'Unexpected train payload')
            require(set(b)=={'weight','bias','mu','scale'},'Unexpected base payload')
            n,real,source=(480,192,144) if inner else (928,352,288)
            require(s['x'].shape==(n,96) and s['real_x'].shape==(real,96),'Training sizes')
            require(torch.equal(s['mu'],b['mu']) and torch.equal(s['scale'],b['scale']),'Base coordinate mismatch')
            require(abs(float(s['mass'].sum())-1)<1e-12 and abs(float(s['real_mass'].sum())-1)<1e-12,'Mass sum')
            require(float((F.one_hot(s['y'],6).double().T@s['mass']-1/6).abs().max())<1e-12,'Class mass')
            idx=torch.cat([torch.arange(source,device='cuda'),torch.arange(source*3,n,device='cuda')])
            require(torch.equal(s['x'][idx],s['real_x']),'Teacher/post ordering differs')
            self.cache[key]=(s,b,idx)
        s,b,idx=self.cache[key]
        if lam==0:
            target=torch.zeros((len(idx),8),device='cuda',dtype=torch.float32)
        else:
            require(arm in {'JP','JG'},'Targets only for associated methods')
            key=(rid,arm)
            if key not in self.cache:
                p=(SOURCE if inner else OUT)/'targets'/rid/('A3.pt' if arm=='JP' else 'A2.pt')
                z=asset(p,rid,'target-P' if arm=='JP' else 'target-G') if inner else own(p)
                if not inner:require(read(p.with_suffix('.json'))['role_id']==rid,'Outer target role')
                require(set(z)=={'target'} and z['target'].shape==(len(idx),8),'Associated target shape')
                require(z['target'].dtype==torch.float32 and torch.isfinite(z['target']).all(),'Target precision/finiteness')
                self.cache[key]=z['target']
            target=self.cache[key]
        return dict(x=s['x'],y=s['y'],mass=s['mass'],real_mass=s['real_mass'],real_index=idx,target=target,
                    W=b['weight'],c=b['bias'],mu=s['mu'],scale=s['scale'])

def canonical_jobs(rs):
    jobs=[]
    for r in rs:
        for recipe in POST_RECIPES:jobs.append(dict(role=r,arm='JC',recipe=recipe,seed=SOURCE_SEED))
        for arm in ['JP','JG']:
            for recipe in RECIPES:
                if recipe['lam']>0:jobs.append(dict(role=r,arm=arm,recipe=recipe,seed=SOURCE_SEED))
    return jobs

def materialize(jobs,pool):
    return [pool.get(j['role'],j['arm'],j['recipe']['lam']) for j in jobs]
