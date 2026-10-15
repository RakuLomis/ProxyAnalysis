"""Trusted packer and a strictly scale-only T interface."""
from common import *

def prepare():
    rows=[]
    for r in contract()['roles']:
        for kind in ['P','G']:
            coeff=parent_asset(PARENT/'C-coefficients'/r['id']/(kind+'.pt'),'coefficients',kind,r['id'],'trusted-packer')
            cuda(coeff['A'],coeff['s']);a=coeff['A']/coeff['s'];m=1+a
            require(bool(torch.isfinite(m).all() and (m>=1).all()),'Invalid metric')
            p=OUT/'scales'/r['id']/(kind+'.pt')
            put(dict(A_over_s=a,M=m),p,role_id=r['id'],kind=kind,scale_only=True,source_sha256=contract()['inputs'][rel(PARENT/'C-coefficients'/r['id']/(kind+'.pt'))]['sha256'])
            for j in range(10):rows.append(dict(role_id=r['id'],kind=kind,feature=FEATURES[j],A_over_s=float(a[j]),M=float(m[j]),D=float(m[j].sqrt())))
    save(pd.DataFrame(rows),OUT/'tables/scales.parquet')

def load(r,arm):
    kind=kind_for(arm);d=own(OUT/'scales'/r['id']/(kind+'.pt'))
    require(set(d)=={'A_over_s','M'},'Scale-only reader received recovery fields')
    require(torch.equal(d['M'],1+d['A_over_s']),'Metric changed');return d['M']

def coefficients(r,arm):
    require(arm!='QT','T recovery-target access forbidden');kind=kind_for(arm)
    return parent_asset(PARENT/'C-coefficients'/r['id']/(kind+'.pt'),'coefficients',kind,r['id'],arm)


