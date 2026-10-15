"""Freeze only C/source legal dependencies. No H queries or labels."""
from common import *
import inspect

def run():
    configure();require(not (OUT/'manifests/seal.json').exists(),'Inventory already sealed')
    fixed={};arts={};parents={}
    def fix(p,h=None):
        h=h or sha(p);require(sha(p)==h,'Historical input changed: '+rel(p));fixed[rel(p)]=h
    def art(p):
        info=read(p.with_suffix('.json'));fix(p,info['sha256']);fix(p.with_suffix('.json'));arts[rel(p)]=info['sha256']
    for root in [TI,SA,CJ]:
        end=read(root/'completion.json');require(end['passed'],'Parent experiment not accepted')
        fix(root/'completion.json');fix(root/'verification.json',end['verification_sha256'])
        p=root/'manifests/experiment-contract.json';fix(p,read(p.with_name('seal.json'))['contract_sha256']);fix(p.with_name('seal.json'))
    close=read(JA/'closeout-20261009/completion.json');require(close['passed'],'Independent JA closeout missing')
    fix(JA/'closeout-20261009/completion.json');fix(JA/'closeout-20261009/verification.json',close['verification_sha256'])
    fix(JA/'failure.json',close['original_failure_sha256']);require(not (JA/'completion.json').exists(),'Historical terminal state altered')
    tc=read(TI/'manifests/experiment-contract.json');jc=read(CJ/'manifests/experiment-contract.json')
    jroles={r['id']:r for r in jc['roles']};roles=[]
    for r0 in tc['roles']:
        r=dict(r0);j=jroles[r['id']]
        require(r['eta']==j['eta'] and r['t']==j['t'],'Parent role parameter mismatch')
        r['C_diagnostic_contents']=j['C_diagnostic_contents'];r['reuse_views']=j['reuse_views'];r['reuse_maps']=j['reuse_maps']
        require(len(r['C_contents'])==16 and len(r['validation_contents'])==6,'Role scope size')
        require(not set(r['C_contents'])&set(r['U_contents']) and not set(r['train_contents'])&set(r['validation_contents']),'Role overlap')
        require(sorted(sum(r['C_diagnostic_contents'],[]))==sorted(r['C_contents']),'Diagnostic content coverage')
        for k in ['C_paired','C_group_pre','C_group_post']:
            p=ROOT/r[k];info=tc['packages'][rel(p)];fix(p,info['sha256']);parents[rel(p)]=info
        for name in ['source-post.parquet','source-pre.parquet']:
            p=PREP/'packages'/r['id']/name;info=tc['packages'][rel(p)];fix(p,info['sha256']);parents[rel(p)]=info
        art(ROOT/r['reuse_views'])
        for p in r['reuse_maps'].values():
            art(ROOT/p);require(read((ROOT/p).with_suffix('.json'))['mapping']['accepted'],'Rejected frozen map')
        roles.append(r)
    require(len(roles)==60,'60 roles required')
    for key in ['historical_source_sha256','source_sha256']:
        for p,h in tc[key].items():fix(ROOT/p,h)
    for p in [JA/'selection/choices.json',JA/'selection/complete.json',CJ/'audits/cohort-and-native.json']:
        fix(p)
    require(read(JA/'selection/complete.json')['actual_target_used'] is False,'Actual target used to select eta')
    audit=read(ROOT/'outputs/mihomo-protocol-audit-20261003/manifest.json')
    fix(ROOT/'outputs/mihomo-protocol-audit-20261003/manifest.json')
    for src in audit['sources']:fix(ROOT/src['local_path'],src['sha256'])
    lb=Path(inspect.getfile(torch.optim.LBFGS))
    env={'python':sys.executable,'torch':torch.__version__,'cuda':torch.version.cuda,
         'gpu':torch.cuda.get_device_name(0),'device':'cuda:0','dtype':'float64','CPU_fallback':False,
         'installed_LBFGS_path':str(lb),'installed_LBFGS_sha256':sha(lb)}
    write(OUT/'environment.json',env)
    c={'version':'AG-stage1-v1','plan_sha256':sha(PLAN),'roles':roles,'rule':RULE,
       'fixed_files':fixed,'artifacts':arts,'parent_packages':parents,
       'source_sha256':{rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')},'environment':env,
       'mapping_cap':480,'classifier_cap':0,'stage_two_authorized':False,'H_numeric_reads_allowed':False,
       'target_U_reads_allowed':False,'PCAP_reads_allowed':False,'physical_post_input_qualified':False,
       'historical_eta_selection_not_fully_independent_of_C_content':True,
       'cohort':{'visits':480,'contents':30,'pairs':23566,'global_content_folds':5,'roles':60}}
    write(OUT/'manifests/experiment-contract.json',c);write(OUT/'manifests/seal.json',{'contract_sha256':sha(OUT/'manifests/experiment-contract.json')})
    write(OUT/'manifests/parent-manifest.json',{'files':fixed,'historical_failure_preserved':True,'protocol_source_files':len(audit['sources'])})
    progress('inventory_complete',roles=60,gpu=env['gpu'],classifier_fits=0)

if __name__=='__main__':run()
