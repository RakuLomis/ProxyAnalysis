"""G2-authorized preregistration and explicit packages; no fit or test selection."""
import argparse
import json
import platform
from common import git
from p3_common import *


def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'model-contract.json').exists()
    p2=read(P2/'independent-verification.json');assert p2['passed']
    prior=read(LATEST/'contract.json')
    for path,h in prior['code_hashes'].items():assert file_hash(ROOT/path)==h
    hashes={**prior['code_hashes']}
    for path in [LATEST/'contract.json',LATEST/'cohort.parquet',LATEST/'global-folds.parquet',
                 LATEST/'predictions.parquet',LATEST/'prediction-seal.json',
                 P2/'pre-only-proxy.parquet',P2/'candidate-eligibility.json',P2/'independent-verification.json']:
        hashes[str(path.relative_to(ROOT))]=file_hash(path)
    # Lock existing generated D0 and E1 model artifacts, never rewrite them.
    for fold in range(5):
        for path in (LATEST/'models'/f'E1-all-f{fold}').iterdir():
            if path.is_file():hashes[str(path.relative_to(ROOT))]=file_hash(path)
    for jobpath in sorted((LATEST/'generator-roles').glob('*.json')):
        job=read(jobpath);write(OUT/'generator-roles'/jobpath.name,job)
        for path in (LATEST/'generation'/job['job']/'paired').iterdir():
            if path.is_file():hashes[str(path.relative_to(ROOT))]=file_hash(path)
    model={'version':'mechanism-center-E1-v1','G2_accepted':True,'human_approval':'同意，请你继续','date':'2026-10-04',
        'git_commit':git('rev-parse','HEAD'),'scope':'E1 W only, five seen deployments, all600/30contents/sixclasses',
        'seeds':SEEDS,'arms':ARMS,'classifier_count':90,'generator_jobs':100,'generator_fits':9500,
        'views':8,'residual_rows':{'paired':72,'cyclic':72,'group':288},'alpha':1.,
        'parameters':{'D0':42,'D1':90,'D2':92},'inputs':{'classifier':W,'D0_pre':W,'D1_D2_pre':W+AUX},
        'center':read(P2/'candidate-eligibility.json')['center_formula'],
        'group':{'beta':'raw post per-content mean, equal weight over four anonymous post visits; pre N/values stay together',
                 'latent_target':'equal-weight mean of four independently encoded post vectors',
                 'residual':'Cartesian4pre x4post per LOCO held content, 288vectors total',
                 'ordering':'pre sort content,W,aux; post independent content,W; no session/repetition in group fit'},
        'cyclic':'original within-content repetition roll(-1), targets used for both beta and latent remainder',
        'scales':'all fitted in inner training; q original log1p(W)+already-logged/ratio aux; zscale ORIGINAL pre phi std',
        'remaining_model':'original alpha1, intercept unpenalized, mean loss per sample, six outputs',
        'sampling':'exact original business-protocol-draw-v1 key and whole-vector residual, no new views/redraws',
        'model':prior['model'],'roles':'original global five folds; each query6contents outside fit18contents; LOCO17',
        'stats':{'primary':['D2_pair-D0_pair','D2_pair-D2_group','D2_pair-M0','D2_pair-D1_pair'],
                 'secondary':['D2_pair-D2_cyclic'],'family_size':4,'bootstrap_draws':10000,'bootstrap_seed':20260928,
                 'cluster':'business-stratified content shared across protocols, seeds and arms',
                 'adjusted_quantiles':[.05/8,1-.05/8],'conditional_on_fixed_models':True,
                 'target':'mean across seeds of five protocol-equal six-class macroF1'},
        'test_selection':False,'TF32':False,'physical_OS_sandbox_claimed':False,
        'distribution_evaluation':'separate worker after all generation frozen; query post scoring only, never generator input',
        'stop_rule':'any startup overflow, missing input, permission failure or CUDA absence stops corresponding task',
        'legacy_hashes':hashes,'P2_scope_limits_retained':True,'Hy2_T_E2_enabled':False}
    write(OUT/'model-contract.json',model)
    write(OUT/'authorization.json',{'G2_accepted':True,'human_approval':'同意，请你继续',
        'scope':'registered P3, 90 E1 classifiers +9500 production Ridge fits, no new branch',
        'contract_sha256':file_hash(OUT/'model-contract.json')})
    cohort=pd.read_parquet(LATEST/'cohort.parquet');aux=pd.read_parquet(P2/'pre-only-proxy.parquet')
    assert len(aux)==600 and aux.session_id.is_unique
    assert np.isfinite(aux[AUX].to_numpy()).all()
    cohort.to_parquet(OUT/'cohort.parquet',index=False)
    negative=0
    for fold in range(5):
        name=f'E1-all-f{fold}';role=read(LATEST/'roles'/(name+'.json'));write(OUT/'roles'/(name+'.json'),role)
        for category,cap,key in [('training','M0','post'),('inference','inference','test_post'),('scoring','scoring','test_labels')]:
            frame=LP.Bundle(LATEST/'packages'/category/name,cap).get(key)
            export(OUT/'packages'/category/name,{key:frame},{'scenario':name})
    for jobpath in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(jobpath);name=job['job'];b=LP.Bundle(LATEST/'packages/generator-paired'/name,'paired')
        pre=b.get('fit_pre');post=b.get('fit_post');query=b.get('query_pre')
        pre=pre.merge(aux,on='session_id',validate='one_to_one');query=query.merge(aux,on='session_id',validate='one_to_one')
        assert len(pre)==72 and len(query)==24 and len(post)==72
        export(OUT/'packages/generator-paired'/name,{'fit_pre':pre,'fit_post':post,'query_pre':query},{'job':name})
        gp=pre[['content_id',*W,*AUX]].sort_values(['content_id',*W,*AUX]).reset_index(drop=True)
        gb=post[['content_id',*W]].sort_values(['content_id',*W]).reset_index(drop=True)
        export(OUT/'packages/generator-group'/name,{'group_pre':gp,'group_post':gb,'query_pre':query},{'job':name})
        group=generator_bundle(job,'group')
        for key in ['fit_pre','fit_post','query_post','test_pre','test_post','labels']:
            try:group.get(key)
            except PermissionError:negative+=1
            else:raise AssertionError('capability escape')
    enable_cuda()
    write(OUT/'environment.json',{'python':platform.python_version(),'torch':torch.__version__,'cuda':torch.version.cuda,
        'gpu':torch.cuda.get_device_name(),'numpy':np.__version__,'pandas':pd.__version__,'conda_env':'Pytorch312'})
    write(OUT/'access-contract.json',{'passed':True,'generator_packages':200,'classifier_roles':5,'negative_checks':negative,
        'test_pre_exported':False,'generator_query_post_exported':False,'group_visit_identity_exported':False,
        'aux_pre_source':file_hash(P2/'pre-only-proxy.parquet'),'classifier_protocol_or_aux_numeric_input':False,
        'software_capabilities_only':True,'independent_package_paths':True})
    doc='''# Extend 机制启发中心实验契约

日期：2026-10-04。G2已获确认，本轮只执行已见五部署E1 W；保留600访问、30内容、六业务、四重复、全局五折。不执行留一协议、T或Hy2分类，不新增采集。本契约在工程重放和业务结果前登记。

## 固定方法与权限

六臂为M0真实post、D0旧paired、D1同增强输入通用paired、D2机制paired、D2group、D2cyclic。D0有42参数，D1有90，D2有92。D1/D2的八个pre统计相同；业务分类器仍只读post六量，不读协议身份、地址、SNI、pre或增强统计。元数据只用于配对、内容划分及审计。

中心每方向以pre正载荷实体数N估计非负beta=sum N*(目标原始字节-pre字节)/sum N²；零分母取0。字节增量固定floor(beta*N+0.5)，P/R保持pre。旧65527P容量若越界则停止，不裁剪重抽。raw中心经原phi编码；Ridge拟合encoded目标减center，保留原pre phi的std及alpha1。beta不是精确协议K，实体数不等于新建物理carrier。

真配使用同次原始post估计beta；cyclic使用原roll(-1) donor；group只使用同内容匿名post原始字节均值估计beta。group的latent目标仍是encoded post的组均值，两种均值不混同；LOCO残差为四pre×四匿名post的Cartesian差，共288向量。group无session/repetition字段，pre自身八统计与其六量一起匿名排序，不借目标身份恢复配对。beta、q尺度、原pre phi尺度和剩余Ridge均在每个内层重新拟合。

生成器拥有fit pre/post和query pre的独立软件权限包，没有query post、test pre/post或标签；group有匿名包。LOCO保留完整内容，不随机拆flow。复用P2注册实体资格，保留5例未见SYN及其仪器条件；不宣称普遍无泄漏或外部盲测。诊断阶段的预检曝光例外仍保留。

## 预算和公平对照

100个生成任务，每方法19次Ridge，五方法合计9500个生产拟合；三seed复用同一拟合，各生成8视图，不改变整向量残差抽样或解码器。D0先与原生成数组、残差池和抽样索引复现。D2各臂的beta只用本臂允许目标，不能共享paired系数。

90个分类器：六臂×五折×三seed。6→32→6 ReLU MLP，422参数，CUDA float32、关闭TF32；1,000步Adam，lr0.001，权重L2=5e-5。每步相同内容/重复槽，0.5真实post CE+0.5辅助CE+L2；M0辅助槽重复真实post。post log1p标准化只由本折480训练post拟合，不测试重新标准化，不早停或选择checkpoint。每seed同初始化、主调度和视图调度；多头批处理不共享模型参数。

## 固定评价与停止

业务四项主要比较为D2pair−D0pair、−D2group、−M0、−D1pair，作为一个新家族；cyclic次要。30内容按六业务分层、跨协议/seed/臂共用10,000 bootstrap抽样，seed20260928，Bonferroni区间分位0.00625/0.99375。主要量为三seed平均的协议等权完整六类macroF1；并报每协议、最差协议、CE bits、Brier、逐类、逐seed及修复/新增错误。区间条件于固定模型，跨零不是等效。

分布诊断在全部生成冻结后由独立评分worker读取训练query post，检查方向MAE、偏差、latent误差及整池经验区间覆盖，不反馈生成器和模型选择。源码规则与本轮经验预测不可互相替代；增强输入或中心有效也不意味着精确封装机制已验证。

CUDA、权限、数值、容量、基线重放或旧哈希失败时停对应任务。没有收益不授权扩模型、删业务或再选中心。文档采用写作技能的证据区分规范；契约与结果分别保存，不覆盖旧实验。
'''
    (DOC/'experiment-contract.md').write_text(doc,encoding='utf-8')
    print('P3 registered: 90 classifiers, 9500 Ridge fits; engineering required before production')


if __name__=='__main__':main()
