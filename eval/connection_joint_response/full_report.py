"""Final classified evidence and independent acceptance; initial gates stay separate."""
from common import *

def run():
    with stage('final_verification_and_report'):
        require((OUT/'stages/score.json').exists(),'Formal scoring not complete')
        c=contract(); extended=read(OUT/'manifests/learning-code.json')
        for p,h in extended['sha256'].items():checked(ROOT/p,h,'frozen-learning-source')
        for p,h in read(OUT/'manifests/scoring-source.json')['sha256'].items():checked(ROOT/p,h,'frozen-scoring-source')
        modelmeta=list((OUT/'models').rglob('*.json')); require(len(modelmeta)==1920,'Classifier count')
        maximum=0.; replay=0.; logs=[]; files={}
        for p in modelmeta:
            d=read(p); log=d['optimizer']; require(log['accepted'],'Unaccepted classifier')
            require(log['device']=='cuda:0' and log['dtype']=='float64','CUDA64 mismatch')
            require(log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000,'Numeric budget mismatch')
            require(all(acceptance_gates(log['objective'],log['initial_objective'],log['max_gradient'],log['iterations'],
                log['objective_replay_error'],log['gradient_replay_error']).values()),'Independent precision audit')
            checked(p.with_suffix('.pt'),d['sha256'],'accepted-classifier')
            maximum=max(maximum,log['max_gradient']); replay=max(replay,log['objective_replay_error']); logs.append(log)
            files[rel(p)]=sha(p); files[rel(p.with_suffix('.pt'))]=d['sha256']
        pooled=pd.read_parquet(OUT/'scores/pooled.parquet'); deployment=pd.read_parquet(OUT/'scores/deployment-mask-scores.parquet')
        primary=read(OUT/'scores/primary.json'); require(primary['family']==5 and primary['CI_coverage']==.99,'Primary family')
        comparisons=pd.DataFrame(primary['comparisons'])
        classes=pd.read_parquet(OUT/'scores/business-scores.parquet')
        dep=deployment.groupby(['target','arm']).mean(numeric_only=True).reset_index()
        worst=dep.groupby('arm').F1_uncovered.min(); pooled['worst_target_F1_U']=pooled.arm.map(worst)
        appendix=DOC/'detailed-appendix-20261010.md'
        endpoints=pd.DataFrame([{k:v[k] for k in ['role_id','arm','parameters','dimensions','seconds','iterations','max_gradient']} for v in logs])
        save(endpoints,OUT/'scores/accepted-endpoints.parquet')
        textfile(appendix,'# 同连接联合响应详细附录\n\n## 分部署及遮蔽\n\n'+deployment.to_markdown(index=False,floatfmt='.6f')+
                 '\n\n## 六业务分项\n\n'+classes.to_markdown(index=False,floatfmt='.6f')+
                 '\n\n## 所有接受分类拟合\n\n'+endpoints.to_markdown(index=False,floatfmt='.6g')+'\n')
        textfile(DOC/'detailed-report-20261010.md',f'''# 同连接联合响应与业务分类实验报告

2026年10月10日。沿用四部署、480访问、30内容、23566排他共同有效TCP对，完成固定八臂业务实验。1920分类拟合全部通过相同CUDA float64数值政策；原P-small、O1及历史实验没有覆盖。

## 设计与权限

M为十统计边际的96维表示。J增加同连接字节事件上下行及字节方向段两块，共162维。I保留J块边际但使用乘积，同为162维；J-S减I-S隔离所选同连接组合，J-S减M-S同时包括新增边际与维数因素。

五全局内容折包含同内容全部部署、重复、两侧及内部连接。每角色三源部署训练post与独立排序pre各288访问；目标C四业务64访问；目标U两业务32训练访问两侧都禁止使用；H六内容24访问只查询post。60角色及八臂共11520预测暴露，不是11520独立访问。

完整原生缓存仅由可信装包器读取；组控制只获取内容token，匿名矩控制连内容token也不获取。学习、生成、缩放和选择不读取目标U，H-pre不进入工作包，全部正式预测封存后才读H标签。字段/API隔离不是操作系统级恶意代码沙箱。

## 训练配置

M/I/J各用两个固定源内容内层留出及四个t候选选择强参照，源CE选择，目标H与U不参与。J六臂共享J-S的t和预处理。目标C的P/G旧96仿射保持冻结，新66维只在四块内映射；eta沿用旧JA2，beta固定0.1。

真实源post、目标C-post、辅助槽CE质量各1/3，small替换辅助槽10%，等于全部CE的1/30。RawPre保留额外pre及标签，RawPost提高源post重复暴露，Marginal使用匿名两侧矩。映射输出是适配统计视图，不能称为物理合法TCP流量。

分类器是六类多项逻辑回归，M为582参数，I/J为978参数。weight L2为0.0005*(1+t)，bias不惩罚。零初始化、可逆预条件化及原坐标梯度验收，max_iter=2000、max_eval=10000。最大原坐标梯度{maximum:.6g}，最大目标重放误差{replay:.6g}。所有训练与推理均CUDA float64。

## 合并成绩

每部署每遮蔽先合并五折，使用完整六类混淆矩阵计算F1，再对部署及遮蔽等权。F1_U不是只在两类U上重新分类。

{pooled.to_markdown(index=False,floatfmt='.6f')}

## 五项预定主比较

六业务分层、每业务5个独立内容，10000次共同内容bootstrap，五项家族99%区间。抽样质量共享于部署、重复、遮蔽及所有方法。

{comparisons.to_markdown(index=False,floatfmt='.6f')}

区间条件于固定模型，不包含重训练变异；反复分析的既有数据不是外部盲测。跨零不是等效，某项通过不能替代其他主比较。

## 分部署

{dep.to_markdown(index=False,floatfmt='.6f')}

六类分项和全部拟合日志见详细附录，全部内容错误翻转见运行根scores/error-flips.parquet。RawPost及Marginal的比较属于次要归因，不扩展本轮确认性家族。

## 与上游概率诊断的区别

C内KP与KG检查逐flow联合状态的条件预测；主P/G映射仍是访问级表示校准。这两个粒度不能混称，条件预测风险不是互信息。初始诊断见implementation-progress-20261010.md，不因上游预测较好就替换分类终点。

## 观测和推广边界

本轮没有新PCAP读取、补采、SS内部chunk或VMess状态恢复。当前extend VLESS没有REALITY或Vision。AnyTLS共享carrier和Hy2 QUIC载体不进入排他TCP矩阵。

O1仍暂停；完整物理post连接重建、独立窗口及无索引在线输入资格未通过。pre是代理会话入口，不是真实直连反事实。本轮不证明精确K、业务语义可逆、全部协议主动防御、跨日期或未见配置泛化。

本候选到此冻结，不根据测试结果继续改箱、beta、eta、模型或业务。所有正负结果保留。
''')
        for p in [OUT/'scores/pooled.parquet',OUT/'scores/deployment-mask-scores.parquet',OUT/'scores/primary.json',
                  OUT/'predictions/visits.parquet',OUT/'scores/scored-visits.parquet',OUT/'scores/error-flips.parquet']:
            files[rel(p)]=sha(p)
        write(OUT/'verification.json',{'passed':True,'files':files,'classifier_fits':1920,'prediction_rows':11520,
              'physical_post_input_qualified':False,'registered_content_isolation':True,'H_pre_worker_rows':0,'target_U_learning_rows':0})
        write(OUT/'completion.json',{'passed':True,'classification_complete':True,'verification_sha256':sha(OUT/'verification.json'),
              'classifier_fits':1920,'physical_post_input_qualified':False})

if __name__=='__main__':run()
