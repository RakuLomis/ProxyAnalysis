"""Report only metadata and synthetic engineering evidence, no new F1 claims."""
from .common import *


def run(out, state):
    s = state["summary"]
    env = read(Path(out) / "manifests/environment.json")
    tests = read(Path(out) / "manifests/engineering-tests.json")
    cov = parquet(Path(out) / "windows/coverage-inventory.parquet")
    ep = parquet(Path(out) / "manifests/endpoint-evidence.parquet")
    files = parquet(Path(out) / "manifests/physical-files.parquet")
    lines = ["# P-small单侧观测验证前置实施报告", "",
        "日期：2026年10月10日。已完成阶段A的来源、角色和元数据检查，以及单侧计算核心与合成测试。当前停在A06，尚未读取PCAP、执行24访问真实先导或生成任何新分类结果。", "",
        "## 已完成范围", "",
        f"旧六臂共360个角色模型的哈希及接受状态已核对；四部署480访问、30内容、五折、60角色保持不变。24访问开发先导按fold0训练内容的每业务首个规范内容和最小重复固定，不依据预测结果选样。", "",
        f"环境为Pytorch312，PyTorch {env['torch']}、CUDA {env['cuda']}、{env['gpu']}。CUDA float64算术检查通过，未安装或升级依赖。", "",
        f"已实现端点确定方向、保守TCP生命周期epoch、窗口冷启动唯一字节计账、FR与新字节方向游程，以及原96维边际直方图汇聚。{tests['tests']}项内存合成测试全部通过。真实流量上的生命周期排他性和覆盖仍需先导验证。", "",
        "提取入口不接收pair名单、受害者pre、NetLog、CDP或标签。元数据阶段显式拒绝打开PCAP及这些内部索引。无正payload连接保留台账但不进入原非空直方图；有payload的失败/背景/未配对连接不因身份被删除。空窗或任何必要统计失效时不输出伪造的合法96维向量。", "",
        "## 元数据覆盖检查", "",
        "| 项目 | 数值 |", "| --- | ---: |",
        f"| 主队列访问 | {s['visits']} |",
        f"| 存在的physical文件 | {s['existing_physical_files']} |",
        f"| 全量文件stat字节 | {s['physical_file_bytes_stat_only']} |",
        f"| 24访问先导stat字节 | {s['pilot_bytes_stat_only']} |",
        f"| 名义导航至browser_quiescent至少30秒 | {s['nominal_30s_compatible_count']} |",
        f"| 独立单调时钟至PCAP时间锚点已核验 | {s['independent_UTC_clock_anchor_count']} |",
        f"| 独立固定窗口连续覆盖已核验 | {s['proven_fixed_window_coverage_count']} |",
        f"| 所选组proxy-info提供非空server与port | {s['proxy_info_endpoint_values_available_count']} |", "",
        f"导航至浏览器结束的名义时长：最小{s['nominal_nav_to_quiescent_seconds']['min']:.6f}秒，中位数{s['nominal_nav_to_quiescent_seconds']['median']:.6f}秒，最大{s['nominal_nav_to_quiescent_seconds']['max']:.6f}秒。这里的browser_quiescent只用于覆盖盘点，不是O2的截断终点。", "",
        "| 部署 | 访问 | 名义时长最小秒 | 名义30秒可容纳 | 端点值可得 |", "| --- | ---: | ---: | ---: | ---: |"]
    for p in PROTOCOLS:
        d = cov[cov.protocol.eq(p)]
        e = ep[ep.protocol.eq(p)]
        lines.append(f"| {p} | {len(d)} | {d.metadata_nominal_nav_to_quiescent_seconds.min():.6f} | {int(d.nominal_30s_before_browser_quiescent.sum())} | {int(e.known_endpoint_values_available.sum())} |")
    lines += ["", "这些时长来自采集端单调时钟。manifest的started_at/completed_at不是与navigation_requested同时采样的时钟对，不能自行转换成精确PCAP窗口。旧prepared-windows的换算来自NetLog，允许用于O1离线诊断，但未移植为O2独立时间证据。", "",
        f"drops登记为{s['drops']}。stopped是采集进程停止完成时刻，不是独立证明捕获持续写入的最后活跃边界；process exit正常也不自动证明固定窗连续完整。", "",
        "## 端点与窗口闸门", "",
        "当前proxy-info中的所选组没有足够的server/port值，尚未建立允许观察的代理IP端口登记。不会从测试pair或flow-index推断端点，也不会读取其他目录的节点凭据。后续需要独立配置/部署记录中的IP和端口白名单，不需要password、UUID或私钥。", "",
        "统一T尚未封存。30秒仅作为名义元数据兼容性参照，不是已经通过的窗口或正式实验参数。O2继续要求起点权限、独立时间换算和真实覆盖依据；不能用浏览器结束截断或最后一个包时间补齐。", "",
        "若现有历史材料无法提供独立时钟依据，可由用户明确授权先做O1-only的24访问工程先导。这是对原同时生成O1/O2先导的范围修订，不能自动执行，也不代表O2合格。O1保留旧窗口，仅定位连接成员与计数实现问题。", "",
        "## 先导文件预算", "",
        "下面只来自文件stat，没有打开文件内容或做PCAP哈希扫描。", "",
        "| 部署 | 先导文件 | 总字节 |", "| --- | ---: | ---: |"]
    pilot = read(Path(out) / "manifests/pilot-visits.json")["visits"]
    pmap = {r["session_id"]: r["protocol"] for r in pilot}
    pf = files[files.pilot].copy()
    pf["protocol"] = pf.session_id.map(pmap)
    for p in PROTOCOLS:
        d = pf[pf.protocol.eq(p)]
        lines.append(f"| {p} | {len(d)} | {int(d.bytes.sum())} |")
    lines += ["", f"先导合计{s['pilot_bytes_stat_only'] / 2**30:.3f} GiB；全量480访问合计{s['physical_file_bytes_stat_only'] / 2**30:.3f} GiB。24文件清单及原路径保存在运行根manifests/physical-files.parquet，并有pilot标志。即使先导通过，全量读盘仍需A17单独确认。", "",
        "## 当前产物与权限", "",
        f"运行根：`{Path(out).relative_to(ROOT).as_posix()}`。包含旧模型来源、角色与父访问、先导清单、480行起点与覆盖台账、端点缺口、文件stat预算、工程测试、源码封存和独立验收。", "",
        "当前真实PCAP读取0，test pre读取0，目标U训练数值包读取0，新分类器拟合0，真实模型推理0。B/C未启动。元数据验收通过只表示来源和合成工程检查通过，不能写成阶段A或物理输入资格通过。", "",
        "## 下一步需要确认", "",
        "1. 提供四部署当时的代理端点IP和端口白名单，或可独立核验它们的非秘密配置来源。", "2. 提供独立采集时钟锚点及活跃覆盖证据；若无法提供，确认是否暂时只执行O1先导，并保留O2未合格。", f"3. 确认是否允许读取预登记24个physical文件，stat合计{s['pilot_bytes_stat_only']}字节，不读取tun，不拟合或评分。", "",
        "旧六臂结果和全部失败记录保持原样。本轮没有新增F1、区间或稳健性成功结论。", ""]
    doc = ROOT / "docs/p-small-observation-validation/metadata-preflight-report-20261010.md"
    if doc.exists():
        raise RuntimeError("report_exists_do_not_overwrite")
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(lines), encoding="utf-8")
    write(out, "manifests/report.json", {"path": str(doc.relative_to(ROOT)), "sha256": sha(doc),
          "scope": "metadata_preflight_only"})
