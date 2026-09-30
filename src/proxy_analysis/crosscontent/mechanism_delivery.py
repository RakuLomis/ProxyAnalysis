"""Static predeclared alpha plots and review-only next-stage job inventory."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .mechanism_contract import verify, read
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def main():
    cfg,business,source,out=verify()
    report=out/'report'
    if not read(report/'validation.json')['passed']: raise ValueError('Audit required')
    for name,expected in read(report/'complete.json')['artifacts'].items():
        if digest(report/name)!=expected: raise ValueError('Report artifact changed')
    dest=out/'delivery'; dest.mkdir(exist_ok=False)
    gains=table(report/'paired-gains.parquet')
    for representation in cfg['representations']:
        fig,axes=plt.subplots(2,4,figsize=(15,7),constrained_layout=True)
        for row,task in enumerate(('six_business','youtube_activity')):
            for col,(protocol,stage) in enumerate((p,s) for p in business['protocols'] for s in ('student','cross')):
                ax=axes[row,col]
                for arm,color in [('M2','#1976b5'),('J-True','#d76b16')]:
                    values=sorted([r for r in gains if r['task']==task and r['protocol']==protocol
                        and r['stage']==stage and r['representation']==representation and r['arm']==arm
                        and r['comparison']=='G_task'],key=lambda r:r['alpha'])
                    x=[0]+[r['alpha'] for r in values]; y=[0]+[r['advantage_bits'] for r in values]
                    ax.plot(x,y,'o-',label=arm,color=color)
                    ax.fill_between(x,[0]+[r['conditional_ci_low'] for r in values],
                                    [0]+[r['conditional_ci_high'] for r in values],color=color,alpha=.12)
                ax.axhline(0,color='gray',linewidth=.7)
                source_name='SS' if protocol=='SHADOWSOCKS' else 'VLESS'
                target_name=('VLESS' if source_name=='SS' else 'SS') if stage=='cross' else source_name
                ax.set_title(f'{task}\n{source_name} -> {target_name}')
                ax.set_xlabel('alpha'); ax.set_ylabel('CE(M0) - CE(student), bits')
                ax.legend(fontsize=8); ax.grid(alpha=.15)
        fig.suptitle(f'{representation}: fixed alpha sensitivity; bands conditional on fitted models')
        fig.savefig(dest/f'{representation}-alpha-curves.png',dpi=150)
        plt.close(fig)
    proposed=[]
    for cohort,schemes in [('240',[1,2]),('299',[0])]:
        for task in ('six_business','youtube_activity'):
            for protocol in business['protocols']:
                for fold in range(5):
                    for scheme in schemes:
                        proposed.append({'cohort':cohort,'task':task,'protocol':protocol,'outer_fold':fold,
                            'scheme':scheme,'representation':'scalar14','alpha':.5,
                            'arms':['M0','M1','M2','M3','J-True','J-Wrong'],
                            'new_teacher_fits':8,'new_student_fits':5+(cohort=='299'),
                            'M0_reuse_requires_identical_training_pool':cohort=='240',
                            'evaluate_same_and_cross_deployment':True,'approved_to_run':False})
    write_json(dest/'next-sensitivity-review.json',{'status':'awaiting_user_confirmation',
        'jobs':proposed,'expected_fits':sum(r['new_teacher_fits']+r['new_student_fits'] for r in proposed),
        'scope':'fixed_all_six_arms_not_selected_by_current_results',
        '299_rule':'source_only_common_round_pool_for_each_teacher_partition; target_valid_test_members_unchanged',
        'no_new_capture':True,'no_300_inclusion':True})
    write_json(dest/'complete.json',{'source_sha256':digest(__file__),
        'artifacts':{p.name:digest(p) for p in dest.iterdir() if p.is_file()}})
    print(json.dumps({'plots':2,'next_stage_jobs':len(proposed),'planned_new_fits':800,'executed':False}))


if __name__=='__main__': main()
