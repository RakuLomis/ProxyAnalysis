"""New independent replay of old batching, not reconstruction of old missing logs."""
from common import *
from train import fit_batch

def compare(a,b):
    rows=[]
    for step in [0,1,10,100,1000]:
        pa=a/('initial.pt' if step==0 else f'step-{step:04d}.pt')
        pb=b/('initial.pt' if step==0 else f'step-{step:04d}.pt')
        x=own(pa,'engineering');y=own(pb,'engineering');s=x['states'][0];t=y['states'][0]
        row=dict(step=step,parameter_max=max(float((s[k]-t[k]).abs().max()) for k in s),
                 logits_max=float((x['logits'][0]-y['logits'][0]).abs().max()),
                 probability_max=float((x['logits'][0].softmax(1)-y['logits'][0].softmax(1)).abs().max()))
        if step:
            for field in ['CE','regularizer','objective']:row[field+'_delta']=float((x[field][0]-y[field][0]).abs())
            row['gradient_max']=max(float((x['gradient_before_clip'][k][0]-y['gradient_before_clip'][k][0]).abs().max()) for k in s)
            row['clipped_gradient_max']=max(float((x['gradient_after_clip'][k][0]-y['gradient_after_clip'][k][0]).abs().max()) for k in s)
            row['Adam_first_moment_max']=max(float((x['Adam'][k]['exp_avg'][0]-y['Adam'][k]['exp_avg'][0]).abs().max()) for k in s)
        rows.append(row)
    return rows

def run():
    with stage('repair_legacy_diagnostic',training=True):
        seal(OUT/'pilot/legacy-code.json',list(Path(__file__).parent.glob('*.py')),passed=True,label='diagnostic code snapshot before backend correction')
        rs=contract()['inner_roles'];actual=contract()['roles'][0]['target']
        first=next(r for r in rs if r['outer']==0 and r['target']==actual and r['calibration']=='vless' and r['group']=='G0')
        second=next(r for r in rs if r['outer']==0 and r['target']==actual and r['calibration']=='vless' and r['group']=='G1')
        job=(first,'A1',0.,20261014);a=OUT/'pilot/legacy/standalone';b=OUT/'pilot/legacy/batched'
        fit_batch([job],publish=False,audit_path=a)
        fit_batch([job,(second,'A1',0.,20261014)],publish=False,audit_path=b)
        rows=compare(a,b);write(OUT/'pilot/legacy-diagnostic.json',dict(new_replay=True,old_missing_values_reconstructed=False,
              rows=rows,final_passed=rows[-1]['probability_max']<=1e-5 and rows[-1]['logits_max']<=1e-4,
              identical_initial_parameters=rows[0]['parameter_max']==0,source_only=True,H_reads=0,U_reads=0))
        progress('legacy_replay_diagnosed',rows=rows)

if __name__=='__main__':run()
