"""Two fixed directions, two fixed steps, independent fully solved endpoints."""
from common import *
import forward as FW
import oracle_bridge as OB

def run_case(r,arm,point,q,center,task_gradient):
    data=task(r,arm); rows=[]; armrows=[]
    for direction,vector in contract()['directions'].items():
        d=tensor(vector); slopes=[]
        for i,h in enumerate(contract()['h']):
            endpoints=[]
            for sign in [1,-1]:
                qp=q+sign*h*d
                require(bool(((qp>=0)&(qp<=2)).all()),'q range failure; no clipping')
                key=f'{point}-{direction}-h{i}-'+('plus' if sign==1 else 'minus')
                endpoints.append(FW.solve(r,arm,qp,key))
            p,n=endpoints
            fd=float((p[1]['Q']-n[1]['Q'])/(2*h))
            fdlo=float((p[0]['Q']-n[0]['Q'])/(2*h))
            signal=abs(float(p[1]['Q']-n[1]['Q']))
            ep=abs(float(p[1]['Q']-p[0]['Q']))+1e-12
            en=abs(float(n[1]['Q']-n[0]['Q']))+1e-12
            efd=(ep+en)/(2*h); identifiable=signal>=10*(ep+en)
            implicit=float(task_gradient@d); limit=1e-5+1e-3*abs(fd)
            error=abs(implicit-fd); leveldiff=abs(fd-fdlo)
            numerical=error<=limit and leveldiff<=limit and efd<=limit/10
            row=dict(role_id=r['id'],arm=arm,point=point,direction=direction,h=h,D_h=fd,D_h_coarse=fdlo,
                     implicit=implicit,error=error,limit=limit,FD_precision_error=efd,signal=signal,
                     signal_floor=10*(ep+en),signal_identifiable=identifiable,numerical_passed=numerical,
                     level_difference=leveldiff,weak_direction=abs(fd)<=limit,
                     passed=identifiable and numerical,Q_plus=float(p[1]['Q']),Q_minus=float(n[1]['Q']))
            rows.append(row); slopes.append(fd)
            for item in OB.direction(data,arm,q,d,h,task_gradient,fd):
                armrows.append(dict(role_id=r['id'],point=point,direction=direction,h=h,**item))
            save(pd.DataFrame(rows),OUT/'FD-cases'/r['id']/f'{arm}-{point}.parquet')
            save(pd.DataFrame(armrows),OUT/'arm-cases'/r['id']/f'{arm}-{point}.parquet')
            if not identifiable or not numerical or not all(a['passed'] for a in armrows):
                return rows,armrows
        scale=1e-5+1e-3*max(abs(s) for s in slopes)
        consistent=abs(slopes[0]-slopes[1])<=scale
        for item in rows[-2:]:
            item.update(step_consistency_error=abs(slopes[0]-slopes[1]),step_consistency_limit=scale,
                        step_consistency_passed=consistent,passed=item['passed'] and consistent)
        save(pd.DataFrame(rows),OUT/'FD-cases'/r['id']/f'{arm}-{point}.parquet')
        if not consistent:return rows,armrows
    return rows,armrows
