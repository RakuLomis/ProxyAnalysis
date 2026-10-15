"""Report measured initial gates, never substitute them for business results."""
from common import *

def run():
    c=contract(); v=read(OUT/'initial-verification.json'); require(v['passed'],'Independent initial audit needed')
    audit=read(OUT/'audits/cohort-and-native.json')
    scores=pd.read_parquet(OUT/'diagnostics/scores/content-scores.parquet')
    # Hierarchical means: C content, then role, then equal deployment. No MI inference.
    byrole=scores.groupby(['target','role_id','block','arm'])[['CE_nats','Brier','unseen_pre']].mean().reset_index()
    byprotocol=byrole.groupby(['target','block','arm'])[['CE_nats','Brier','unseen_pre']].mean().reset_index()
    save(byprotocol,OUT/'diagnostics/scores/summary.parquet')
    pooled=byprotocol.groupby(['block','arm'])[['CE_nats','Brier','unseen_pre']].mean().reset_index()
    pool=pooled.to_markdown(index=False,floatfmt='.6f'); per=byprotocol.to_markdown(index=False,floatfmt='.6f')
    textfile(DOC/'implementation-progress-20261010.md',f'''# 同连接联合响应实施进度

2026年10月10日。已完成计划A01至A18：新实验契约、原生缓存与96维重放、联合表示、匿名控制、角色权限测试，以及C训练区的固定条件分布诊断。八臂业务分类尚未完成，以下分布预测数字不是业务F1。

## 数据与输入

四部署SS、VLESS、Trojan、VMess，480访问、30独立内容、23566排他共同有效非空TCP对，原五个全局内容折不变。M为96维，J为162维同连接联合表示，I为162维对应边际乘积表示。

历史M重放最大误差为{audit['M_replay_error']:.3g}，门限1e-14。已通过{v['tests']}项信息、匿名控制、角色成员、查询字段和CUDA推理检查。合成反例中，M与I相同而J不同；这验证新表示保留了一种旧边际遗漏的组合，不证明业务收益。

可信装包器读取已封存完整原生连接缓存，为60角色生成2640工作包。完整缓存不是学习器输入。每个角色的目标U两侧和H-pre均不出现在学习工作包；目标H标签在全部正式分类预测封存前被拒绝读取。权限通过字段白名单和读取API执行，不是操作系统级对恶意代码的沙箱。

没有读取PCAP、没有重新划窗或删除成员。O1暂停、O2未启动。注册实体未发现跨折，不等于已证明全部物理TCP epoch均完整且唯一。物理post输入资格仍未通过。

## 联合条件响应

每角色只在目标C内进行四折内容留出，12内容拟合、4内容评分。四块各使用M0、真实flow对应KP、匿名内容组合KG，相同平滑与内容访问连接层级质量，共2880小型计数参照。拟合和预测使用CUDA float64，实际留出C-post只在全部诊断预测封存后用于评分。

以下均值先按C内容，再按角色和部署等权。它们属于有限离散模型的对数风险及Brier，不是互信息或真实条件熵，也没有进入业务分类特征、可靠性权重、箱选择或调参。

{pool}

## 分部署诊断

{per}

## 后续数值先导

下一阶段为固定外折0的12角色，288个M/I/J源内选择分类器和96个八臂外层分类器，共384个，计入1920总拟合预算。beta固定0.1，eta沿用旧JA2，分类t只按固定源内容CE选择。测试H不用于先导评分或修改方案。

训练和推理强制Pytorch312 CUDA float64，保持原坐标梯度与目标重放验收、2000迭代及10000函数评价上限。先导完成后报告耗时与剩余预算；目前不能从上述条件响应诊断推断新业务增益。

独立初始验收：`{rel(OUT/'initial-verification.json')}`。原结果和暂停O1产物均未覆盖。
''')
    textfile(DOC/'feature-schema.md','''# 同连接联合表示字段

原96维保存W上下行、U上下行、P上下行、E上下行、FR_packet_runs和R_unique_zero_runs的分别归一化分布。新66维由两个17格字节事件块与两个16格字节交互块构成。

字节事件块每方向保留空方向一格；正方向U切点1024、16384、262144，E切点4、16、64。字节交互块使用U_total切点2048、32768、524288及run切点4、16、64。区间左闭右开，每块和为1。

I保留对应块边际并改为乘积，J保留同连接组合。U是已观测唯一TCP字节，E是正新字节到达事件，不是chunk数。FR和唯一run保持各自定义，不从记录时间重命名。

模型只接受匿名visit token加对应数值列；visit token不参与数值计算。IP、端口、SNI、协议身份、路径、内容文本、配对ID与测试pre被排除。连接集合及父访问仍来自离线关联整理，独立单侧窗口资格尚未验证。
''')
    textfile(DOC/'protocol-mechanism-and-observation-boundary.md','''# 协议机制与观测边界

机制依据使用采集客户端74cfed919c03f07a21b252328fe48b72c5361215及封存依赖，Meta参考88dcbf7f1614a67c3b36b848ee3592dfa92ada36不能回填历史运行。

SS当前为AES-256-GCM无plugin与smux；VLESS当前TCP加TLS，无REALITY及Vision；Trojan为TCP加TLS；VMess为WS加TLS、auto安全模式、global padding关闭。源码提供分块、首写、封装及有条件padding假设，不提供捕获中的内部块数或远端实现真值。

AnyTLS共享TLS carrier及复用状态，Hy2为QUIC加Salamander共享carrier，两者未进入本轮排他TCP业务矩阵。不能把TCP E或U直接替换到这两种载体，亦不能将内部writeConn计数当抓包事件数。

观测单位、离线共同有效成员与物理post攻击资格分别登记。完整缓存装包不代表学习器有权限读取目标U或测试pre。概率诊断与分类是两个终点，不生成精确K、initial/relay或互信息主张。
''')
    progress('initial_report_written',classification_results_available=False)

if __name__=='__main__':run()
