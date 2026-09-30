import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .common import *
from ..targeted_diagnostics.run import mdtable


def implementation_notes():
    files=read(OUT/'implementation-sources.json');lines=['# 历史实现与可观测性证据','',
        '以精确 commit 获取官方源码，不以最新版本替代；只读核验。所有源码 SHA256、URL 和本地缓存路径在 implementation-sources.json。', '',
        '重要纠正：go.mod 中存在 sing-vmess 依赖，但本次追踪的 VLESS TCP 调用链实际进入 Mihomo 仓库内 transport/vless/vision。sing-vmess 的实现只作为依赖证据保存，不用它替代实际代码路径。', '',
        '调用链：adapter/outbound/vless.go 的 TCP 分支先建立 TLS/REALITY 连接，再调用 transport/vless/conn.go；后者检查 XRV 并构造本仓库 vision.NewConn。该实现读写 padding 控制，按内部命令及状态切换 direct 路径。源码存在该路径与某条捕获实际发生该状态切换是不同证据。', '',
        '因此，本轮只能从连续 TCP 字节观测到可解释的记录语法和明文 Hello 起点，不能从长度、段数 +2 或第一次 application_data 直接识别 Vision initial/relay 边界。post 中合法的记录语法也不能保证之后每条都属于同一外层加密层。', '',
        '协议基础：[RFC 8446 §5](https://www.rfc-editor.org/rfc/rfc8446.html#section-5)。记录解析不等于解析受保护的内部类型或控制命令。', '', '## 源码定位','']
    tokens={'transport/vless/conn.go':['case XRV:','vision.NewConn'],
            'transport/vless/vision/conn.go':['readLastCommand =','case commandPaddingDirect:','direct read start','direct write start'],
            'transport/vless/vision/vision.go':['func NewConn','ExtendedReader:','underlying.NetConn()'],
            'transport/vless/vision/padding.go':['commandPaddingContinue','commandPaddingEnd','commandPaddingDirect','func ApplyPadding'],
            'adapter/outbound/vless.go':['// default tcp network','func (v *Vless) streamTLSConn'],
            'transport/vmess/tls.go':['GetRealityConn']}
    evidence=[]
    for f in files:
        if f['status']!='ok' or f.get('repository')!='MetaCubeX/mihomo':continue
        text=Path(f['local_path']).read_text(encoding='utf-8').splitlines()
        for token in tokens.get(f['path'],[]):
            nums=[i+1 for i,s in enumerate(text) if token in s]
            if nums:
                url=f"https://github.com/{f['repository']}/blob/{COMMIT}/{f['path']}#L{nums[0]}"
                lines.append(f"- [{f['path']}:{nums[0]}]({url})：`{token}`。")
                evidence.append({'file':f['path'],'token':token,'lines':nums,'url':url,'sha256':f['sha256']})
    js('implementation-locations.json',evidence)
    (DOC/'implementation-evidence.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def atlas():
    directory=DOC/'timeline-atlas';directory.mkdir(exist_ok=True)
    manifest=load('parse-sample-manifest');timelines=load('event-timelines');records=load('record-observations');terms=load('termination-events')
    pages=[]
    for index,((sid,cid),g) in enumerate(manifest.groupby(['session_id','connection_id'],sort=True)):
        meta=g.iloc[0];name=f'connection-{index+1:03d}.png'
        fig,axs=plt.subplots(2,3,figsize=(14,7),layout='constrained')
        for row,side in enumerate(['pre','post']):
            r=timelines[(timelines.session_id==sid)&(timelines.connection_id==cid)&(timelines.side==side)].sort_values('run_index')
            early=r[r.run_index<12];color=['C0' if d==1 else 'C1' for d in early.direction]
            axs[row,0].bar(early.run_index,early.new_bytes*early.direction,color=color)
            axs[row,0].set_yscale('symlog');axs[row,0].set_xlabel('First 12 runs (not protocol records)');axs[row,0].set_ylabel(side+' signed new bytes')
            axs[row,1].scatter(r.first_time_ns/1e9,r.direction*r.new_bytes,s=8,c=['C0' if d==1 else 'C1' for d in r.direction])
            axs[row,1].set_yscale('symlog');axs[row,1].set_xlabel(side+' seconds from capture first packet');axs[row,1].set_title('Whole connection, run start times')
            q=terms[(terms.session_id==sid)&(terms.connection_id==cid)&(terms.side==side)&terms.rst]
            for t in q.relative_time_ns:axs[row,1].axvline(t/1e9,color='red',ls=':',alpha=.5)
            re=records[(records.session_id==sid)&(records.connection_id==cid)&(records.side==side)&(records.record_index<12)]
            for d,rr in re.groupby('direction'):
                axs[row,2].scatter(rr.complete_available_ns/1e9,rr.record_index+.12*d,marker='^' if d==1 else 'v',color='C0' if d==1 else 'C1',s=18,label='upload' if d==1 else 'download')
                for rec in rr.itertuples():
                    if rec.content_type!=23:axs[row,2].annotate(str(rec.content_type),(rec.complete_available_ns/1e9,rec.record_index+.12*d),xytext=(3,3*d),textcoords='offset points',fontsize=7)
            axs[row,2].set_xscale('symlog',linthresh=.05)
            if len(re):axs[row,2].legend(fontsize=7,title='Unlabelled: type 23',title_fontsize=7)
            axs[row,2].set_title('First 12 record syntax units / direction');axs[row,2].set_xlabel(side+' seconds, symlog (complete availability)');axs[row,2].set_ylabel('Record index; labels=other content types')
        fig.suptitle(f"{index+1:03d} {meta.batch} {meta.protocol} {meta.mechanism_group} / {meta.load_layer} / {meta.partition}\nIndependent side clocks; red dotted lines = RST; no inferred phase cut")
        fig.savefig(directory/name,dpi=115);plt.close(fig)
        pages.append(dict(case=index+1,session_id=sid,connection_id=cid,batch=meta.batch,protocol=meta.protocol,group=meta.mechanism_group,partition=meta.partition,figure=name))
    save('atlas-index',pages)
    (directory/'index.md').write_text('# 有限样本时间/记录图谱\n\n全部选定连接均展示；没有按清晰程度挑图。完整累计字节进度见 event-timelines.parquet。零点按侧定义，不可视为跨侧对齐。\n\n'+
        '\n'.join(f"- [{p['case']:03d} {p['batch']} {p['protocol']} {p['group']} {p['partition']}]({p['figure']})" for p in pages)+'\n',encoding='utf-8')


def report():
    DOC.mkdir(parents=True,exist_ok=True);figdir=DOC/'figures';figdir.mkdir(exist_ok=True)
    z=load('connection-load-table');strata=load('load-strata-summary');models=load('model-summary');pe=load('phase-evidence');manifest=load('parse-sample-manifest')
    budget=read(OUT/'budget.json');fits=read(OUT/'fit-audit.json');logs=read(OUT/'phase-log-audit.json')
    evidence=pe.groupby(['protocol','partition','side','evidence_level','parse_status'],as_index=False).size()
    save('phase-evidence-summary',evidence)
    record_summary=load('record-observations').groupby(['batch','side','direction','record_index','content_type'],as_index=False).agg(
        records=('start','size'),median_payload=('record_payload_length','median'),median_first_ns=('first_observation_ns','median'),median_available_ns=('complete_available_ns','median'))
    save('record-index-summary',record_summary)
    rst=load('termination-events');rst=rst[rst.rst]
    ending=rst.merge(pd.read_parquet(BASE/'tcp-byte-ledger.parquet')[['session_id','connection_id','side','direction','curve_duration_ns']],on=['session_id','connection_id','side','direction'],validate='many_to_one')
    ending['relative_capture_progress']=ending.relative_time_ns/ending.curve_duration_ns.where(ending.curve_duration_ns>0)
    save('rst-timeline-summary',ending.groupby(['batch','protocol','side','direction'],as_index=False).agg(
        rst_events=('packet_ordinal','size'),median_relative_progress=('relative_capture_progress','median'),median_time_ns=('relative_time_ns','median')))
    fig,axs=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    for ax,((b,p),g) in zip(axs.flat,z.groupby(['batch','protocol'])):
        for d,q in g.groupby('direction'):ax.scatter(np.log2(1+q.pre),q.difference,s=4,alpha=.35,label=f'dir={d} n={len(q)}')
        ax.set_yscale('symlog');ax.set_title(b+' '+p);ax.set_xlabel('log2(1+pre unique bytes)');ax.set_ylabel('Post - pre unique bytes');ax.legend(fontsize=7)
    fig.savefig(figdir/'load-difference.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,d in zip(axs,[-1,1]):
        for b,g in strata[(strata.protocol=='VLESS')&(strata.direction==d)].groupby('batch'):
            g=g.set_index('load_bin').reindex(['zero','(0,4KiB)','[4,16KiB)','[16,64KiB)','[64,256KiB)','[256KiB,1MiB)','[1MiB,inf)'])
            ax.plot(range(len(g)),g['median'],marker='o',label=b)
        ax.set_xticks(range(7),['zero','<4K','4-16K','16-64K','64-256K','256K-1M','>=1M'],rotation=25,fontsize=8)
        ax.set_title('VLESS '+('download' if d==-1 else 'upload'));ax.set_ylabel('Connection median additional bytes');ax.legend(fontsize=8)
    fig.savefig(figdir/'vless-load-centers.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,d in zip(axs,[-1,1]):
        q=models[(models.protocol=='VLESS')&(models.scope=='run_common')&(models.direction==d)]
        q.pivot(index='batch',columns='model',values='mae').plot.bar(ax=ax,rot=0)
        ax.set_ylabel('OOF connection-weighted MAE (bytes)');ax.set_title('Download' if d==-1 else 'Upload')
    fig.savefig(figdir/'descriptive-oof.png',dpi=150);plt.close(fig)
    implementation_notes();atlas()
    primary=pd.read_parquet(ROOT/'outputs/content-generalization-20260916/business-01/primary-cohort.parquet')
    identity=primary.merge(z[['session_id','content_group','fold']].drop_duplicates(),on='session_id',validate='one_to_one')
    assert identity.groupby('content_id').fold.nunique().eq(1).all()
    pred=load('oof-residuals')
    assert not pred.duplicated(['session_id','connection_id','direction','scope','model']).any()
    assert len(pred[(pred.scope=='byte_all')&(pred.model=='M0')])==len(z)
    assert manifest.groupby('content_group').partition.nunique().eq(1).all()
    expected=pd.read_parquet(BASE/'tcp-byte-ledger.parquet').merge(manifest[['session_id','connection_id','side']],on=['session_id','connection_id','side'],validate='many_to_one')
    assert int(expected.rst_count.sum())==len(rst)
    js('validation.json',{'passed':True,'primary_registered_contents_single_fold':True,'primary_visits_checked':len(identity),
                         'oof_unique_and_complete':True,'sample_content_partitions_disjoint':True,'RST_counts_reproduce_ledger':True,'no_E2_features_generated':True})
    root=ET.parse(OUT/'tests.xml').getroot();suites=list(root.iter('testsuite'))
    tests={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','errors','failures','skipped']};assert tests['errors']==tests['failures']==0
    js('tests.json',tests)
    for f,h in read(OUT/'contract.json')['inputs'].items():assert digest(f)==h
    code=[*Path(__file__).parent.glob('*.py'),ROOT/'tests/unit/test_early_stage_mechanism.py',ROOT/'eval/protocol_normalization/run_early_stage_mechanism.py']
    js('provenance.json',{'code':{str(f):digest(f) for f in code},'inputs_unchanged':True,'classifier_fits':0,
        'outputs':{f.name:digest(f) for f in OUT.glob('*.parquet')},'descriptive_fits':fits})
    text=['# VLESS 早期阶段机制候选：实施结果','', '日期：2026-09-24。三个批次独立报告；未补采、未全量重扫、未改阈值或旧 240 访问队列。', '',
        '## 结论','',
        '本轮支持“连接级附加量及方向段差存在部署相关的集中模式”，但没有取得 initial/relay 的独立语义边界。记录语法可解析不等于阶段可识别；因此没有生成分阶段校正 K，也没有删除固定头部或两段。', '',
        '0916 VLESS 上行在 <4 KiB 和 4–16 KiB 两个主要负载箱中位附加量均为 1,870 bytes（分别 1,085、350 条连接）；更大上行箱仅 21、14、1 条，≥1 MiB 为空，不能外推任意大负载。下行各非零负载箱中位约 5,702–6,240 bytes，≥1 MiB 有 76 条，说明集中现象不只出现在小流，但各箱中心并不完全相同。', '',
        '在共同段资格集合、内容分组 OOF 中，0916 VLESS 上行 M0/M1/M2 的 MAE 分别为 152.79/152.43/151.82 bytes；下行为 446.32/446.41/440.92 bytes。新增关系项改善有限，不能因此认定附加量是精确常数，更不能证明其来自握手。0914 的方向结果及条目等权指标全部保留如下。', '',
        f"冻结样本 {budget['pairs']} 对连接/{budget['files']} 文件，{budget['bytes']:,} bytes（{budget['bytes']/2**20:.2f} MiB）；实际为 45 对 VLESS、12 对 SS，空分层未补样本。VLESS 两侧共 180 条方向流均建立初始 Hello 与连续记录语法解析，但证据等级只到 E1，不到 E2。SS 24 条方向/侧各自保留为无 cipher 解析的参照。", '',
        '实现核验纠正了一个容易混淆的点：本次 VLESS 走 Mihomo 自带 transport/vless/vision，而不是仅因 go.mod 存在就认定使用 sing-vmess 的 Vision 实现。实现能指出控制命令/切换状态，但本轮捕获未提供经验证的命令位置。', '',
        '## 1. 权限、资格与分组','',
        f"有效字节连接方向 {len(z):,} 行；描述性成功拟合 {fits['descriptive_successful_fits']} 次，失败 {fits['descriptive_failed_fits']} 次；分类器拟合 0。空折不拟合，记录在 descriptive-models.json。", '',
        '所有连接随父访问和同 URL 内容分组；全数据新建稳定哈希五折，非原 240 队列分类折。对旧 primary 注册 content_id 又核对同内容同折。跨批次相同 URL 共用身份；URL 仅用于分组、其哈希存入表，不进入回归。metadata 和配对差值不作为攻击模型输入。', '',
        '字节集合只需同方向两侧 U 有效；段模型须同连接四方向侧均有效。结束状态只用已有 FIN/RST 标记，不重做上一轮四格筛选，也不把它们当因果解释。1 KiB=1024 bytes。', '',
        '## 2. 负载分层','',mdtable(strata),'','![负载散点](figures/load-difference.png)','',
        '![VLESS 分箱中心](figures/vless-load-centers.png)','',
        'median/MAD/IQR 为连接等权；item_equal_median 先访问内连接中位、再条目内重复中位、最后条目等权中位。不是访问总附加量。零负载单列，稀疏/空箱不隐藏。', '',
        '## 3. 描述性模型','',
        'M0=训练中位常数；M1=常数+log2(1+入口字节)；M2 再加入口方向段数及两侧 FIN/RST。M1/M2 使用固定 LAD 线性目标、固定次序去除共线列；所有拟合/尺度/常数都在该折训练内容计算，无超参搜索。全样本拟合仅为描述，主误差使用 OOF。', '',
        mdtable(models),'','![OOF](figures/descriptive-oof.png)','',
        'byte_all 与 run_common 分开；M0/M1/M2 只能在 run_common 内直接比较。MAE 与 item_equal_mae 分别为连接等权和访问→条目等权，不将连接当独立访问。内部交叉拟合不是外部机制验证。', '',
        '## 4. 固定样本和时间/记录定位','',mdtable(load('sample-cell-coverage')),'',
        '按双侧 Δrun 分组抽样是事后诊断，不代表总体发生率。VLESS 每格 discovery/verification 各最多一条；SS 每格最多一条。先冻结清单、来源哈希和规则，再读取捕获；没有解析失败后替换样本。', '',
        '[全部 57 对连接图谱](timeline-atlas/index.md)。每图并列两侧前 12 段、完整连接段时间线和前 12 条记录语法单位；红虚线为 RST。全量 150,052 段的侧内时间、首个新字节零点和累计字节进度保存在 event-timelines.parquet。首包时钟和首字节时钟分开，不代表两侧共同物理事件，也未用逐时刻差值寻找切点。', '',
        '## 5. 独立证据与可观测性','',mdtable(evidence),'',
        '[历史实现、精确版本与源码定位](implementation-evidence.md)。post 的记录语法可以延续通过不同处理路径，不能把解析到尾部解释成始终同一外层 TLS；更不能把第一个 type=23 当作握手结束/转发开始。没有内部密钥或受验证阶段标记时，阶段保持未知。', '',
        f"对所选 VLESS 访问的保留 trace/journal 检查源码中明确的 Vision direct/padding 日志字样：状态 {logs['status']}，匹配数 {logs.get('matched_lines','NA')}，文件数 {logs.get('files','NA')}。只保留计数/哈希，不导出日志正文。这只针对所选保留日志，不声称所有可能日志都不存在。", '',
        '### RST 时间线（只作结束现象）','',mdtable(load('rst-timeline-summary')),'',
        '### 初始两条记录语法单位','',mdtable(record_summary[record_summary.record_index<2]),'',
        '记录表含字节区间、首次观测时间、完整可用时间和包来源；乱序时两个时间不一定相同。TCP 序号重组经过区间和载荷重叠一致性检查；缺口不补零，不任意重同步。原始载荷只在内存，不保存 SNI、endpoint、凭据或明文正文。', '',
        '## 6. 阶段门与最终状态','',
        'E0–E8 完成描述/解析与证据分级；本轮 E2 语义证据行数为 0，因此 E9 条件不成立，未生成 initial/relay 特征。E10 输出 unavailable 权限，post-only_phase 只有 post 参数且不返回虚构边界；这不是获得了可用的 post-only 规范化方法。', '',
        '本轮没有发现充分阶段证据，不等于证明早期阶段不贡献附加量。若要继续，需要不同的独立证据或明确的新测量问题；不能用最相似切点、固定减 2 或同数据低残差来填补机制缺口。', '',
        f"测试：{tests['tests']} 项通过，{tests['failures']} 失败、{tests['errors']} 错误。旧输入哈希未变；既有方向段重建、OOF 行唯一性、内容分组、预算及主队列内容一致性审计通过。条件分阶段字节拆分/合并未实施，故不宣称验证了不存在的 E9 功能。", '',
        '复用入口：`python eval/protocol_normalization/run_early_stage_mechanism.py <tables|models|sample|sources|parse|report|all>`。报告与实验产物位于独立目录；本轮到此停止，不启动分类训练。']
    (DOC/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    (DOC/'next-gate.md').write_text('# 停止门\n\nE0–E8 的预定测量已完成，E11 报告交付。E2 语义阶段证据为 0；E9 条件不成立，E10 为 unavailable。没有阶段校正 K、没有分类训练。\n\n可保留的结论是连接附加量与段差的部署相关模式，以及记录语法可观察但语义阶段尚未独立定位。任何新的日志权限、密钥、样本扩展、切分方法或分类训练均需另行确认。\n',encoding='utf-8')
    js('stage-status.json',{'E0_E8':'completed_observation_and_evidence_grading','E9':'not_applicable_no_E2_evidence','E10':'unavailable_permission_audit','E11':'complete','classifier_fits':0,'K_generated':False})
    print('E11 report complete:',DOC/'report.md',flush=True)
