"""Run auditable A--F validation and stop before activity-task learning."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import platform
import subprocess
import sys
import time

import yaml

from .data import build_data, digest, write_json, OBSERVATION
from .experiments import classification, recoverability, summarize


def report(out, data, labels, cls, reg, info, smoke):
    lines = ['# 信息论方向第一阶段：证据桥接与标签审计', '',
             '本报告不包含业务Y分类、teacher训练或语义解耦实验。', '',
             f'运行类型：{"单折冒烟验证，不解释性能" if smoke else "完整分组OOF基线"}。', '',
             '## 观察与数据边界', '',
             f'- 观察层级：`{OBSERVATION}`。数值来自post，但窗口/实体选择借助采集索引；不是已验证可部署post-only。',
             '- 主分析只含SS/VLESS严格一对一TCP；Hy2不进入同类变换预测。',
             '- C为本次部署标签，不是与节点/配置分离的纯协议效应。',
             '- 14个单侧标量、17个Δ候选量；域名等只用于分组/标签。', '',
             '| 设置 | 会话 | URL |', '|---|---:|---:|']
    for setting, rows in data.items():
        lines.append(f'| {setting} | {len(rows)} | {len({r["target_domain"] for r in rows})} |')
    lines += ['', '## 标签证据：Y=站点×业务活动', '',
              '以下媒体标签仅按明确播放证据审核；页面加载不是播放。其他站点只记录可验证的page_load，尚未替用户指定更细活动标签。', '',
              '| 站点 | 最终访问 | 正片播放已证实 | 未证实且目标未达 | 无充分播放证据 | 正片已证实且页面代理候选 | 独立内容数 |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for domain in ['bilibili.com', 'youtube.com', 'vimeo.com']:
        group = [r for r in labels if r['site_domain']==domain]
        count = Counter(r['playback_status'] for r in group)
        lines.append(f'| {domain} | {len(group)} | {count["passed"]} | {count["not_met"]} | {count["unverified"]} | '
                     f'{sum(r["playback_verified"] and r["page_proxy_candidate"] for r in group)} | '
                     f'{len({r["content_id"] for r in group})} |')
    lines += ['', '## 部署分类主结果', '',
              'LORO整轮留出；LOUO整URL留出。logistic内层同类分组选择C，ExtraTrees为固定预算敏感性。先验与模型使用同一OOF样本。', '',
              '| 划分 | 输入 | 模型 | n | macro-F1 | balanced accuracy | log-loss(bits) |',
              '|---|---|---|---:|---:|---:|---:|']
    for r in cls:
        if r['setting']=='primary' and r['model'] in {'logistic', 'prior', 'extra_trees'}:
            lines.append(f'| {r["scheme"]} | {r["view"]} | {r["model"]} | {r["n"]} | '
                         f'{r["macro_f1"]:.3f} | {r["balanced_accuracy"]:.3f} | {r["log_loss_bits"]:.3f} |')
    lines += ['', '## post→Δ：主要模型与对照', '',
              '全局均值为普通基线；oracle_C/U/UC享有部署/URL标签，只从训练样本计算。留URL时U/UC均值退回训练全局均值。'
              '代数基线直接用log(post)减训练log(pre)均值，专门揭示共享项带来的预测收益。', '',
              '| 划分 | Δ目标 | 模型 | MAE | R² |', '|---|---|---|---:|---:|']
    for r in reg:
        if r['setting']=='primary' and r['target_view']=='delta' and r['model'] in {
            'global_mean', 'oracle_C_mean', 'ridge_post', 'ridge_post_drop_family', 'algebra_global'}:
            score = f'{r["r2"]:.3f}' if r['r2'] is not None else 'NA'
            lines.append(f'| {r["scheme"]} | {r["metric"]} | {r["model"]} | {r["mae"]:.4g} | {score} |')
    lines += ['', '## 信息论操作量', '',
              '以下为经验交叉熵/Fano代入量，不是精确互信息，也不是总体置信下界。负交叉熵差保留。'
              'delta_condition_U仅是已见U条件预测诊断，允许U进入条件模型；不是主模型。', '',
              '| 划分 | 视图 | H(C)−CE(bits) | Fano plug-in(bits) |', '|---|---|---:|---:|']
    for r in info:
        if r['setting']=='primary' and r['model']=='logistic':
            lines.append(f'| {r["scheme"]} | {r["view"]} | {r["entropy_minus_ce_plugin_bits"]:.3f} | {r["fano_plugin_bits"]:.3f} |')
    lines += ['', '## 预注册敏感性：logistic', '',
              '| 设置 | 划分 | 视图 | n | F1 | log-loss(bits) |', '|---|---|---|---:|---:|---:|']
    for r in cls:
        if r['setting']!='primary' and r['model']=='logistic':
            lines.append(f'| {r["setting"]} | {r["scheme"]} | {r["view"]} | {r["n"]} | {r["macro_f1"]:.3f} | {r["log_loss_bits"]:.3f} |')
    lines += ['', '## 限制与停止节点', '',
              '- URL bootstrap只描述固定OOF输出的URL变化，不能反映完整训练和共同轮次不确定性；逐轮与去轮汇总另表。没有将fold视为独立样本检验。',
              '- 原生尺度ridge为预先固定的轻量模型，失败不等于信息不存在；没有调参直至得到正结果。',
              '- 距离目标执行了同家族剔除，但未重提完整分布做置换耦合实验；该项仍待扩展，不能据此宣称完全排除数学耦合。',
              '- 同一站点主要一个内容，跨内容共有活动泛化尚不可验证。',
              '- 到G1：需要确认可验证活动类别及补采集选择；不自动用page_load替代video_playback，不启动Y模型。', '',
              '所有OOF、允许列、划分、排除理由和证据摘要位于本目录。']
    (out / 'first-stage-validation-report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root', type=Path, default=Path('outputs/detailed-5reps'))
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--config', type=Path, default=Path('configs/information_validation.yaml'))
    parser.add_argument('--spec', type=Path, default=Path('configs/reproducibility.yaml'))
    parser.add_argument('--target-contract', type=Path,
                        default=Path('Datasets/TrafficTracer-Detailed-5Reps/sites_detailed.yaml'))
    args = parser.parse_args()
    out = args.output_root
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    config_path = args.config
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    config['smoke'] = args.smoke
    if args.smoke:
        config['settings'] = config['settings'][:1]
    metric_path = args.spec
    metrics = yaml.safe_load(metric_path.read_text(encoding='utf-8'))['metrics']
    sites_path = args.target_contract
    sites = yaml.safe_load(sites_path.read_text(encoding='utf-8'))
    paths = [config_path, metric_path, sites_path, *sorted(Path('src/proxy_analysis').rglob('*.py')),
             *sorted(Path('tests').rglob('*.py')),
             *[args.input_root/n for n in ['run_registry.parquet', 'routing_eligibility.parquet',
                                           'repeat_feature_long.parquet', 'feature-contract.json']]]
    state = subprocess.run(['git', '-c', f'safe.directory={Path.cwd().as_posix()}', 'status', '--short'],
                            capture_output=True, text=True, check=True).stdout
    write_json(out/'environment.json', {'python': sys.version, 'executable': sys.executable,
        'platform': platform.platform(), 'dependencies': {p: importlib.metadata.version(p)
            for p in ['numpy', 'scipy', 'scikit-learn', 'pyarrow', 'PyYAML']}})
    write_json(out/'provenance.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'cwd': str(Path.cwd()), 'argv': sys.argv, 'git_status': state,
        'hashes': {str(p): digest(p) for p in paths}, 'effective_config': config})
    (out/'observation-contract.md').write_text(
        '# 观察契约\n\n数值pre/post各自来自实体包，但配对、实体集合、方向与会话边界来自采集索引。'
        'SS/VLESS过滤为一对一TCP；Hy2排除主模型。所有结果标为offline_index_assisted_post。'
        'domain仅作标签/分组，metadata仅独立诊断；部署可用分段未验证。\n', encoding='utf-8')
    print('prepare data and activity evidence', flush=True)
    data, scalar, delta, labels = build_data(args.input_root, out, config, metrics, sites)
    print('cohorts', {k: len(v) for k,v in data.items()}, flush=True)
    cls = classification(data, scalar, delta, config, out)
    reg = recoverability(data, scalar, config, metrics, out)
    cs, rs, info = summarize(cls, reg, config, out)
    report(out, data, labels, cs, rs, info, args.smoke)
    write_json(out/'validation-summary.json', {'status': 'completed', 'smoke': args.smoke,
        'elapsed_seconds': time.monotonic()-start, 'classification_oof_rows': len(cls),
        'regression_oof_rows': len(reg), 'final_sessions_label_audited': len(labels),
        'runtime_checks': ['registry_unique', 'route_unique', 'metric_unique', 'grid_unique',
                           'outer_group_isolation', 'OOF_unique_per_setting'],
        'unit_tests': 'see separately recorded pytest output; not asserted by this runner',
        'stop': 'G1_label_evidence_and_coverage_before_Y_training'})
    write_json(out/'result-artifacts.json', {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p)}
                                           for p in sorted(out.iterdir()) if p.is_file()})
    print('complete', out, flush=True)


if __name__ == '__main__':
    main()
