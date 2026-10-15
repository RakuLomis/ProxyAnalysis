from core import *

def table(frame,decimals=6):
    def val(x):
        if isinstance(x,(float,np.floating)):return f'{x:.{decimals}f}'
        return str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |']+
                     ['| '+' | '.join(val(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])

FAMILIES=[
 ('AH','0916','docs/0916-A-H-mechanism-evidence-synthesis.md','outputs/mechanism-evidence-0916',240,30,'SS/VLESS historical deployments','157-dimensional visit statistics','source classifier; statistical/decision calibration','exact visits vs cyclic donors vs content-deployment centers','both sides and labels within training content; post-only inference','C improves B/D; F improves C; F/G/H do not establish exact identity advantage','No stable external transfer or pairing necessity theorem'),
 ('AH-cross','0916','docs/0916-source-calibration-cross-deployment-results.md','outputs/source-calibration-cross-deployment-0916/run-01',240,30,'SS/VLESS historical deployments','157-dimensional visit statistics','source-only deployment to other deployment','exact vs content centers','only source deployment fits; global held-out contents; target post inference','Directional transfer benefits; not bidirectionally robust','Not externally blind, direct-to-proxy or protocol causal'),
 ('R-T','0916','docs/record-time-business-0916/formal-results.md','outputs/record-time-business-0916/run-01/formal',120,30,'VLESS historical deployment','strict record structure plus independent new-byte time','six-business supervised / VICReg pretraining','exclusive flow pairs vs same-content cross-repeat flows','supervised post; SSL side access by arm; global content folds','Record representation benefits; exact pair pretraining does not exceed strong supervised S2','Not semantic record matching or unseen deployment'),
 ('R-T-probe','0916','docs/record-time-business-0916/localization/summary.md','outputs/record-time-localization-0916/run-01',120,30,'same VLESS as R-T','frozen flow embedding and visit pooling','frozen small nonlinear heads','same L1-L4 frozen source encoders and random control','training content heads only; no encoder updates; post test','Pair representation readable but below post-only/side SSL controls','Not evidence that all downstream nonlinear reads are impossible'),
 ('CB','0916','docs/paired-calibration-budget-0916/summary.md','outputs/paired-calibration-budget-0916/run-01',240,30,'SS/VLESS historical deployments','seven-variable visit summaries','limited pair calibration and extra pre content','exact versus donor controls','C two sides; U pre and label only; U post isolated','Extra contents help small post baseline; stable advantage over extra raw pre not established','No quantified real capture/label savings'),
 ('FSC','0916','docs/feasible-summary-calibration-0916/summary.md','outputs/feasible-summary-calibration-0916/run-01',240,30,'SS/VLESS historical deployments','feasible seven-variable summary coordinates','cross-business missing-post augmentation','exact vs group/cyclic; center and marginal also pair-derived','C other business pairs; U pre and labels; test real post','Paired beats raw and group in both deployments under original corrected families','No generally best generator or full-target reference superiority'),
 ('Extend-v3','Extend','docs/extend-calibration-20260930/v3-experiment-contract.md','outputs/extend-calibration-20260930/run-01/extraction-03/formal-01',600,30,'SS/VLESS/Trojan/VMess/AnyTLS; Hy2 ineligible','W six-dimensional / T seven-dimensional visit summaries','within-deployment missing-business-post augmentation','exact versus anonymous group; center/marginal still pair-based','same C and U pre/labels; U post forbidden; full-post reference separate','W five deployments and T four pass registered raw/group comparisons','Not six-protocol classification, unseen deployment or independence from pairing of marginal'),
 ('Unified','Extend','docs/business-protocol-eval-extend/formal-results.md','outputs/business-protocol-eval-extend/run-01',600,30,'five eligible W deployments','six-variable W numeric summary','E1 shared model / E2 leave-one deployment','paired augmentation vs group and raw pre mix','E1 mixed source post; E2 target unavailable; global content exclusion','Paired beats group but reliable increment over strong post mix not established','E2 is fitting-time exclusion, not researcher-blind external protocol test'),
 ('Probability','Extend','docs/protocol-probability-drift/formal-report.md','outputs/protocol-probability-drift-20261004',480,30,'four exclusive TCP deployments; qualified current configs','ten binned connection statistics','conditional probability and information measurement','exact connection joint table vs content-side products','train-content kernels; content-held-out probability scores','Exact joint kernels improve declared probability scores','No business classifier benefit or full channel information / precise overhead K'),
 ('KSR','Extend','docs/kernel-sensitivity-regularization/formal-report.md','outputs/kernel-sensitivity-regularization-20261005/run-01',480,30,'SS AES-GCM / VLESS TCP TLS / Trojan TCP TLS / VMess WS TLS','96-dimensional marginal histograms','within-deployment post LR with kernel geometry regularization','exact vs anonymous group and post-repeat covariance','same allowed training post labels; kernels use legal training pairs','No corrected advantage over fair strong L2 or group kernel','Not evidence of information-theoretically optimal post model'),
 ('DSR','Extend','docs/drift-state-group-risk/complete-report-20261006.md','outputs/drift-state-group-risk-20261005',480,30,'four TCP deployments','96-dimensional marginal histograms','drift-state group-risk regularization','exact / group / post-state controls','nested contents; same post labels; selected zero controls retained','Positive candidates ran, all outer alpha zero; no new gain','Identical final predictions are not statistical equivalence proof'),
 ('RW','Extend','docs/cross-fitted-drift-reweighting/complete-report-20261006.md','outputs/cross-fitted-drift-reweighting-20261006',480,30,'four TCP deployments','96-dimensional marginal histograms','cross-fitted task-aware fixed reweighting','exact state vs group vs post-CE state','OOF train-only difficulty; test real post; fixed label-informed weights','Parameters/predictions changed but full gain criterion failed','Not label-free drift or evidence that constraints were ignored'),
 ('CT-v4','Extend','docs/calibrated-deployment-business-transfer/v4/detailed-final-report-20261007.md','outputs/calibrated-deployment-business-transfer-20261006/run-04',480,30,'four current qualified TCP configs','connection kernels to 96-dimensional visit marginal histograms','auxiliary-business-calibrated deployment transfer','exact connection vs group product kernel','source full business library; target C four businesses; target U both sides forbidden','CT4 beats CT1/CT3 but below same-target-permission StrongPost','Not best single-side attack, target-free transfer or universally useless pairing'),
 ('JA','Extend','docs/joint-affine-transfer/detailed-experiment-report-20261009.md','outputs/joint-affine-transfer-20261007/run-01',480,30,'same four current TCP deployments as CT','96-dimensional visit marginal histograms','auxiliary calibration joint conditional-mean adaptation','exact visit vs same-content full-donor mean','CT permissions unchanged; selected maps and classifiers frozen','JA1 beats raw pre but not group/block/StrongPost increment criteria','Cannot revoke CT connection result or equate affine mean with full joint probability model'),
 ('B-SSL','Extend','docs/mechanism-conditioned-ssl-extend/formal-results.md','outputs/mechanism-conditioned-ssl-extend/run-01',600,30,'five qualified W deployments','six-window-statistic encoder with train-only mechanism conditions','conditioned pair SSL, frozen readouts and post fine-tuning','exact visit vs group; side-only and same-architecture controls','train-content cross-fit conditions; pre/conditions deleted for post inference','One of five primary comparisons positive; full main claim not met','High pair retrieval does not prove superior post representation or business gain'),
 ('J-post','Extend','docs/post-anchored-paired-training-extend/formal-results.md','outputs/post-anchored-paired-training-extend/run-01',600,30,'same five W deployments','six-window-statistic encoder and post business head','task-aware pre auxiliary decisions / post-anchored consistency','exact visit vs group and post consistency','both train sides and labels; conditions train-only; post-only inference','J4 obtains no corrected positive interval among six primary comparisons','Not justification to change weight, labels or classifier without a new information object'),
 ('G-kernel','Extend','docs/drift-kernel-business/formal-report.md','outputs/drift-kernel-business-20261005/run-01',480,30,'four exclusive TCP deployments','connection kernels and 96-dimensional visit marginal histograms','kernel-induced business probability distributions','exact connection vs anonymous content products','training content labels and kernels; frozen post probability decisions','Eight template-control contrasts positive; none of eight strong direct-post comparisons positive','Kernel score preservation is not competitive single-side attack performance')]

def evidence():
    rows=[]
    for key,batch,report,output,visits,contents,config,representation,task,granularity,permissions,support,limit in FAMILIES:
        p=ROOT/report;require(p.exists(),'Evidence report missing: '+report)
        root=ROOT/output
        files=[]
        if root.exists():
            # Only small declared provenance/summary directories, never raw captures or credentials.
            for parent in [root,root/'manifests',root/'contract',root/'audit',root/'report',root/'run-01',root/'run-01/manifests']:
                if parent.exists():
                    files.extend(v for v in parent.glob('*.json') if any(t in v.name for t in ['contract','completion','complete','seal','verification','validation','provenance','claim-ledger','metrics','contrasts']))
            for parent in [root,root/'scores',root/'comparisons',root/'run-01',root/'run-01/scores',root/'run-01/comparisons']:
                if parent.exists():files.extend(v for v in parent.glob('*.parquet') if any(t in v.name for t in ['summary','metrics','primary','contrast','pooled']))
        files=sorted(set(files))
        policies={'AH':'95% uncorrected content-bootstrap; no equivalence margin',
            'AH-cross':'Original two-direction comparisons; retained source report family and intervals',
            'R-T':'2000 business-stratified content draws; uncorrected descriptive 95%; three fixed seeds',
            'R-T-probe':'2000 business-stratified content draws; uncorrected descriptive 95%; fixed models',
            'FSC':'10000 content draws; four primary comparisons; 98.75% Bonferroni intervals',
            'Extend-v3':'10000 business-stratified content draws; W family 10 and T family 8 separately',
            'Unified':'10000 content draws; E1 and E2 separate three-comparison families; not joint six-test guarantee',
            'Probability':'10000 content draws; eight primary probability comparisons; no classifier endpoint',
            'KSR':'Twelve prespecified deployment-comparison family; pooled mean not a new test',
            'RW':'10000 content draws; three-comparison Bonferroni 98.333333%; by-deployment 95% descriptive',
            'CT-v4':'10000 content draws; three-comparison Bonferroni 98.333333%; fixed selected models',
            'JA':'10000 content draws; four-comparison Bonferroni 98.75%; fixed selected models'}
        policies.update({'B-SSL':'10000 business-stratified content draws; five-comparison family, 99% intervals',
                         'J-post':'Original six-comparison corrected family; fixed three seeds and models',
                         'G-kernel':'Eight primary comparisons; additional eight strong-post comparisons kept separate'})
        classifiers={'AH':'fixed linear source classifier, reused across B/C/D/F/G/H; separate post E',
            'AH-cross':'same fixed linear source classifier and registered affine calibration',
            'R-T':'two-branch 32-channel CNN flow encoder; 65->32->6 visit head',
            'R-T-probe':'frozen same flow encoder; train-only 65->32->6 nonlinear head',
            'CB':'7->32 ReLU->6 MLP; fixed 1000 Adam steps',
            'FSC':'7->32 ReLU->6 MLP; fixed 1000 Adam steps',
            'Unified':'6->32 ReLU->6 MLP; E1/E2 shared weights; independent I0 control',
            'Probability':'no business classifier; discrete conditional kernel',
            'KSR':'96->6 multinomial LR; 582 parameters',
            'DSR':'96->6 multinomial LR; fixed state-risk candidates',
            'RW':'96->6 multinomial LR; fixed OOF reweighting plus protection',
            'CT-v4':'96->6 multinomial LR with frozen v4 numeric policy',
            'JA':'96->6 multinomial LR with same v4 numeric policy'}
        classifiers.update({'Extend-v3':'W 6 / T 7 ->32 ReLU->6 MLP, registered original budgets',
                            'B-SSL':'6->64->32 encoder plus 32->32->6 business head; 3782 deployed parameters',
                            'J-post':'same 3782-parameter deployed encoder/head; train-only condition branch deleted',
                            'G-kernel':'fixed kernel-induced six-class probabilities; direct-post probability and MLP controls'})
        rows.append({'family':key,'dataset':batch,'visits':visits,'global_contents':contents,'configuration_scope':config,
            'visit_scope':'W 600 / T four-deployment 480 subset' if key=='Extend-v3' else str(visits),
            'repetition_ids':[1,2,4,5] if batch=='0916' else [1,2,3,4],
            'classifier':classifiers.get(key,'Registered original classifier; see linked source'),
            'representation':representation,'task':task,'correspondence_granularity':granularity,'training_permission':permissions,
            'prediction_input':'pre query -> post probability score; no business attack classifier' if key=='Probability' else 'post only; AH A/pre and explicit offline diagnostics excluded',
            'split':'global content folds; all repeats/sides/internal flows together',
            'interval_policy':policies.get(key,'Original family and model-conditional intervals from linked report; no new pooled test'),
            'independent_retraining_this_round':False,'status':'report describes completed scientific work; JA additive closeout separately recorded',
            'machine_evidence_status':'registered files located' if files else 'report only; no new machine completion asserted',
            'report':report,'report_sha256':C.sha(p),'support':support,'boundary':limit,
            'machine_files':[{'path':C.rel(v),'sha256':C.sha(v)} for v in files]})
    write(OUT/'evidence-index.json',{'rows':rows,'new_fits':0,'cross_dataset_F1_curve_prohibited':True})
    save(OUT/'claim-matrix.parquet',pd.DataFrame([{k:v for k,v in r.items() if k!='machine_files'} for r in rows]))
    return rows

def run():
    with stage('synthesize'):
        require((OUT/'figure-manifest.json').exists(),'Figures prerequisite')
        rows=evidence();a=pd.read_parquet(OUT/'moment-decomposition.parquet');inner=a[a.inner.notna()]
        p=pd.read_parquet(OUT/'decision-projections.parquet');p=p[p.inner.notna()]
        scopes=p.groupby(['classifier_arm','scope','eta'])[['mapping_effect_MSE','relative_logit_effect_MSE','probability_L1_mean','mapped_view_class_change_mass']].median().reset_index()
        means=inner.groupby(['calibration','eta'])[['within_norm','between_norm','delta_matrix_norm','C_effect_MSE','delta_stable_rank']].median().reset_index()
        actual=pd.read_parquet(OUT/'actual-post-candidate-comparisons.parquet')
        actual['partition']=np.where(actual.inner.isna(),'outer-common-eta-selected','source-inner-fixed-t0')
        rec=pd.read_parquet(OUT/'matched-candidate-recovery.parquet').groupby(['inner','calibration','eta','arm'],dropna=False).MSE.mean().reset_index()
        save(OUT/'summary-by-deployment-eta.parquet',means);save(OUT/'projection-summary.parquet',scopes);save(OUT/'matched-recovery-summary.parquet',rec)
        algebra=C.read(OUT/'algebra-verification.json');close=C.read(CLOSE/'verification.json')
        coverage=pd.read_parquet(OUT/'outer-eta-coverage.parquet')
        summary='# 精确访问身份增量分解与研究结项报告\n\n2026年10月9日。保持原JA科学设计和全部模型不变，本轮完成追加工程结项、同正则分解、冻结决策投影和跨实验证据整理。新增分类器及映射拟合均为0。\n\n'
        summary+='## 工程结项与数学核验\n\n'
        summary+=f'原CT5读取错误已在独立后处理入口兼容：420项历史和180项新模型CUDA float64重放误差为0，评分及10000次bootstrap与旧独立报告完全一致。原failure保留，修订completion仅存在于追加结项目录。全部模型、映射、槽位和历史工作包重新核对哈希，复用已绑定实现的全量数值验收。\n\n2880对内层与49对外层同正则映射均通过核验；归一化最大误差{algebra["normalized_max"]:.3e}，原门为1e-10。60个外层中另有11个选择不同eta，不能直接按访问内项归因。\n\n'
        summary+=r'$$C_{BA}=C_{\mathrm{between}}+C_{\mathrm{within}},\quad M_1-M_2=C_{\mathrm{within}}(S_{AA}+\alpha I)^{-1},\quad b_1-b_2=-(M_1-M_2)\mu_A.$$'+'\n\n'
        summary+='JA2保留同内容中心之间的关系和全部入口协方差；JA1额外使用同内容内、同次访问两侧波动的交叉项。该恒等式已在当前保存模型上数值验证，不再只是代数猜测。它不证明访问残差是纯噪声，也不等于互信息估计。\n\n'
        summary+='## 访问内关系的幅度与正则作用\n\n以下对每角色先计算，再按校准部署与eta报告内层角色中位数；不是2880个独立实验。尺度来自各角色post训练标准化，不能混合原坐标矩阵作物理或因果解释。\n\n'+table(means)+'\n\n'
        summary+='![固定四正则作用](figures/within-effect-by-eta.png)\n\n四eta全部保留；更大eta对同一角色的差算子施加更强收缩，但不把小eta或大within范数自动判为最佳。内容间和访问内矩阵通常非正定，范数平方含交叉项，不能用范数比例计算“对应信息占比”。\n\n'
        at1=means[means.eta.eq(1)].set_index('calibration')
        summary+=f'在固定eta=1面板中，SS的校准视图变化MSE中位数为{at1.loc["shadowsocks","C_effect_MSE"]:.6f}，VLESS为{at1.loc["vless","C_effect_MSE"]:.6f}，Trojan为{at1.loc["trojan","C_effect_MSE"]:.6f}，VMess为{at1.loc["vmess","C_effect_MSE"]:.6f}。这说明精确身份不是在映射中被完全忽略。其差矩阵稳定秩中位数约在{means.delta_stable_rank.min():.2f}至{means.delta_stable_rank.max():.2f}之间；稳定秩仅描述奇异值能量集中程度，不是协议状态数或信息论维度。\n\n'
        bb=pd.read_parquet(OUT/'block-effects.parquet');bb=bb[bb.inner.notna()&bb.eta.eq(1)]
        tops=bb.groupby(['output_block','input_block']).C_effect_energy.mean().nlargest(10).reset_index()
        summary+='固定eta=1下十个最大平均块作用项如下；全100块、所有eta保留在原表，不据此挑选下一轮特征。块作用能量存在跨输入块交叉项，不能将这十项简单相加成总贡献。\n\n'+table(tops)+'\n\n![角色归一块幅度](figures/cross-block-effects.png)\n\n'
        summary+='## 冻结决策投影\n\n固定内层t=0，分别使用JA1与JA2已保存的分类器，各自冻结。下表是映射视图变化，不是新攻击F1；概率变化与类别翻转只说明同一冻结读出对两个映射的敏感性。外层使用49个共同eta角色的各自最终分类器，t差单独登记。\n\n'+table(scopes)+'\n\n'
        summary+=r'$$\Delta s(x)=P_6W(M_1-M_2)(x-\mu_A).$$'+'\n\n'
        summary+='![映射与相对分数变化](figures/mapped-view-and-decision.png)\n\n较大投影不是正确分类收益；较小投影也不是所有业务信息不存在。源库pre可用于训练视图诊断，留出pre仅用于封存后的离线诊断。源post分数方差及逐真类相对分数完整保存在表中，不把这些离线伪预测当作真实post测试。\n\n'
        summary+='## 与原分类证据的关系\n\n'
        summary+='JA1实际测试接口输入真实post，没有在测试时应用pre到post映射。两方法最终分类器由不同辅助视图训练而来；本轮未反事实重训。因此，冻结投影和实际post错误翻转的并列是机制定位线索，不能证明某个within坐标导致了F1变化。\n\n'
        summary+='既有CT4相对CT1及CT3的正向区间成立，低于StrongPost的负向区间同样成立。JA1优于CT1，但未建立相对JA2、JA0或StrongPost的完整优势。恢复MSE改善、映射改变和业务增益必须分开。\n\n![选择后恢复与实际业务](figures/recovery-and-actual-classification.png)\n\n'
        summary+='## 同候选与最终选择的区别\n\n'+table(actual.groupby(['partition','calibration','eta'],dropna=False)[['F1_U_delta','repair','added_error','prediction_changed']].mean().reset_index())+'\n\n'
        summary+='这些是每24访问小角色的描述性均值，不替代合并五折OOF的原主指标。F1差取未覆盖两类，错误修复、新增及翻转计数则覆盖全部24访问、六类。内层使用同eta、同t=0；外层49角色eta相同但t可能不同，内外层分区单列。不要从该表选择下一轮eta或宣称新的显著性。完整60角色覆盖见附录；11个不匹配角色没有被悄悄从原JA结论中删除。\n\n'
        summary+='## 当前研究判断\n\n精确关系确实增加了访问内跨侧协方差，而组关系并非没有跨侧知识。当前仿射解能把这一差精确定位；现有分类证据却不支持将“这项统计关系存在”直接推成“当前模型超过强post参照”。这支持冻结当前利用方式，不支持宣布代理关联无信息或普遍无益。\n\n下一步不新增损失、网络或正则搜索。是否重开方法，需要一个过去摘要未表达、真实对应可标定且post端能利用的新信息对象，并同时升级公平强post输入。\n\n'
        summary+='## 产物与复现\n\n代码位于`eval/paired_identity_closeout/`；解释证据位于`outputs/paired-identity-decomposition-20261009/run-01/`；追加结项位于`outputs/joint-affine-transfer-20261007/run-01/closeout-20261009/`。报告区间全部继承原实验，没有新主检验。详见[逐项附录](detailed-appendix.md)、[跨实验主张证据边界](evidence-synthesis.md)和[重开条件](information-object-reopening-checklist.md)。\n'
        textfile(DOC/'detailed-report.md',summary)
        appendix='# 精确身份分解详细附录\n\n## 外层正则覆盖\n\n'+table(coverage)+'\n\n## 冻结投影完整部署分项\n\n'
        appendix+=table(p.groupby(['classifier_arm','scope','calibration','eta'])[['mapping_effect_MSE','relative_logit_effect_MSE','probability_L1_mean','mapped_view_class_change_mass','source_post_relative_logit_variance']].median().reset_index())
        appendix+='\n\n## 同候选留出恢复\n\n'+table(rec)+'\n\n## 验收\n\n```json\n'+json.dumps(algebra,ensure_ascii=False,indent=2)+'\n```\n'
        textfile(DOC/'detailed-appendix.md',appendix)
        synthesis='# 代理关联研究的主张证据与边界\n\n已有证据支持条件性用途，不支持关联普遍成功或普遍无用。当前最强攻击增量目标仍未完成；测量价值不能替代它，但分类负结果也不能抹去准确测量和对应建立的价值。不同批次、表示、监督权限和区间家族分别列出，不构造成跨实验F1提升曲线。\n\n'
        for row in rows:
            synthesis+=f'## {row["family"]} 证据\n\n'
            synthesis+=f'范围：{row["dataset"]}，{row["visits"]}访问，{row["global_contents"]}个全局内容；{row["configuration_scope"]}。\n\n任务与表示：{row["task"]}；{row["representation"]}。对应粒度：{row["correspondence_granularity"]}。\n\n权限：{row["training_permission"]}。\n\n支持：{row["support"]}。\n\n边界：{row["boundary"]}。\n\n来源：[原报告]({(ROOT/row["report"]).as_posix()})；机器证据与哈希见evidence-index.json。\n\n'
            synthesis+=f'分类器：{row["classifier"]}。统计：{row["interval_policy"]}。观测分母：{row["visit_scope"]}；重复编号：{row["repetition_ids"]}。本轮不重训。\n\n'
        synthesis+='## 不能再反复使用的解释\n\nCT和JA已限制目标未覆盖业务两侧权限，不能只说目标post过于充分。RW确实改变参数和预测，不宜一概归为约束未使用。JA允许全矩阵，但仍没有完成强参照增量；这只关闭当前仿射摘要候选，不证明所有联合对象建模不可能。记录级输入曾产生明确表示收益，不能把它与配对SSL独立增量混为一谈。\n\n'
        ct=pd.read_parquet(C.V4/'comparisons/primary-contrasts.parquet')
        unified_path=ROOT/'outputs/business-protocol-eval-extend/run-01/primary-contrasts.parquet'
        unified=pd.read_parquet(unified_path)
        synthesis+='## CT与统一模型的原主比较\n\n以下直接读取封存机器表，区间家族不同，不合并检验。CT为三比较家族；统一模型E1和E2各自三比较，次要循环控制只给原普通区间。\n\n'+table(ct)+'\n\n'+table(unified)+'\n\n'
        save(OUT/'historical-CT-primary.parquet',ct);save(OUT/'historical-unified-primary.parquet',unified)
        synthesis+='## 保留的总体主张\n\n真实连接对应可以支持更准确的跨侧变换估计，并在部分受限迁移管线中优于原样入口与粗对应控制；在已研究的权限、表示和部署条件下，尚未形成稳定超过充分或适配强post参照的完整方案。内部内容隔离、代码追溯和大量模型不能替代外部验证，也不能消除同一内容长期反复开发造成的选择风险。\n'
        textfile(DOC/'evidence-synthesis.md',synthesis)
        textfile(DOC/'information-object-reopening-checklist.md','# 新信息对象研究重开条件\n\n当前暂停96维摘要方法族，不宣布代理关联研究不可能。重开须用户确认一个新的有限计划，并满足：\n\n1. 指定旧边际直方图没有保留的新关系。\n2. 给出实际观测来源、封装层、配置前提、缺失处理及post可生成性。\n3. 说明精确关系为何优于同内容集合标定，以及公平组控制。\n4. 说明post-only任务接口，不能以恢复或MI代替业务证据。\n5. 新输入同时给强post参照。\n6. 固定内容隔离、权限、预算、内层选择、主比较及停止条件。\n\n可候选保留连接多变量联合状态，但本轮没有提取新表示或训练。SS实际chunk、VMess内部块和initial/relay没有被本轮恢复。\n')
        write(OUT/'method-family-freeze.json',{'frozen':True,'scope':'Existing 96D marginal histogram probability templates, affine means, kernel regularization and drift reweighting',
            'new_fits':0,'not_a_universal_impossibility_theorem':True,'CT_positive_pairing_results_preserved':True,
            'reopening_requires_user_confirmation_and_new_observable_information_object':True,'original_primary_decisions_unchanged':True})
if __name__=='__main__':run()
