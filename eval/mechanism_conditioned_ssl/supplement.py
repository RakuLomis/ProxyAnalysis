"""Preregistered descriptive probe intervals and independent score cross-check.

Added after prediction sealing; changes no training, predictions, draws, family,
or inference permissions. Its own source seal is separate from the fit seal.
"""
from common import *


def main():
    cli(__doc__).parse_args(); authorize()
    assert read(OUT/'report-manifest.json')['complete']
    baseline_hash = sha(OUT/'oof.parquet')
    write(OUT/'supplement-seal.json', {'source_sha256': sha(Path(__file__)),
          'parent_fit_seal': sha(OUT/'seal.json'), 'prediction_sha256': baseline_hash,
          'purpose': 'complete planned descriptive diagnostics; no new fit or primary contrasts'})
    a = pd.read_parquet(OUT/'aggregate-metrics.parquet'); boot = np.load(OUT/'bootstrap.npz', allow_pickle=False)
    point = a.set_index(['stage', 'arm', 'head']).F1.to_dict(); result = []
    for hk in ['linear', 'mlp']:
        for ref in [v for v in SOURCES if v != 'B5']:
            delta = boot[f'probe|B5|{hk}']-boot[f'probe|{ref}|{hk}']; ci = np.quantile(delta, [.025, .975])
            result.append({'head': hk, 'contrast': 'B5-'+ref,
                           'delta': point['probe', 'B5', hk]-point['probe', ref, hk],
                           'low95': ci[0], 'high95': ci[1], 'primary': False})
    result = pd.DataFrame(result); result.to_parquet(OUT/'probe-contrasts.parquet', index=False)
    error = pd.read_parquet(OUT/'error-transitions.parquet')
    details = error.groupby(['reference', 'protocol', 'content_id', 'label_id'])[['repaired', 'new_error']].sum().reset_index()
    details.to_parquet(OUT/'content-error-transitions.parquet', index=False)
    # Independent library implementation verifies points and selected original draws.
    from sklearn.metrics import f1_score
    pred = pd.read_parquet(OUT/'scored-oof.parquet'); metrics = pd.read_parquet(OUT/'per-protocol-seed-metrics.parquet')
    deviations = []
    for row in metrics.itertuples(index=False):
        g = pred[pred.stage.eq(row.stage) & pred.arm.eq(row.arm) & pred['head'].eq(row.head)
                 & pred.seed.eq(row.seed) & pred.protocol.eq(row.protocol)]
        value = f1_score(g.truth, g.guess, labels=list(range(6)), average='macro', zero_division=0)
        deviations.append(abs(value-row.F1))
    contents = sorted(pred.content_id.unique()); draw_errors = []
    for d in [0, 1, 9999]:
        weights = np.bincount(boot['content_indices'][d], minlength=30)
        for arm in ARMS:
            points = []
            for (seed, protocol), g in pred[pred.stage.eq('finetune') & pred.arm.eq(arm)].groupby(['seed', 'protocol']):
                sw = np.array([weights[contents.index(c)] for c in g.content_id])
                points.append(f1_score(g.truth, g.guess, labels=list(range(6)), average='macro', zero_division=0, sample_weight=sw))
            draw_errors.append(abs(np.mean(points)-boot[f'finetune|{arm}|mlp'][d]))
    assert max(deviations) < 1e-12 and max(draw_errors) < 1e-12
    write(OUT/'independent-score-check.json', {'passed': True, 'point_checks': len(deviations),
          'bootstrap_draw_checks': len(draw_errors), 'maximum_point_error': max(deviations),
          'maximum_draw_error': max(draw_errors), 'library': 'sklearn.metrics.f1_score',
          'prediction_unchanged': sha(OUT/'oof.parquet') == baseline_hash})
    summary = '''## 结果解释与固定诊断补充

B5最终部署等权F1为0.780593，是本轮最高点估计；但相对普通post SSL的+0.006760、通用中心的+0.003302、匿名组的+0.011485，其预登记五项家族校正区间均跨零。相对B0的+0.012146也在校正后跨零。只有相对2000步监督B0L的+0.013618边界通过，校正下界约+0.000007，非常接近零；不能将这一有限结果表述为全面、稳健的机制配对优势。

冻结读出也没有显示B5稳定占优：B5线性F1为0.665009，接近随机E的0.662261，低于group的0.667107；B5冻结MLP为0.746133，低于通用条件B4的0.751558、随机E的0.751450及group的0.750074。这里只是点序，下面按原预登记描述性口径给出普通95%区间，不纳入最终五项家族。随机非线性特征本身具有业务可读性，因此不能把任意SSL高于机会水平当作预训练增量。

最终B5的CE为1.107235 bits，Brier为0.316050，均未优于B4的1.082292和0.314895，也未优于B3的1.065742和0.314896。业务决策、概率质量与上游关系不是同一终点。B5最差部署F1为0.752253，点估计优于各参照；但AnyTLS和SS的B5 F1低于B4，不能以最差部署改善掩盖逐部署例外。

本轮支持继续保留一个可执行、权限清晰的机制条件化表示候选，不支持宣称机制与精确配对已共同建立相对普通SSL和通用中心的独立业务收益。固定摘要、训练日程与反复研究的数据限制继续保留。没有据此新增方法、模型或参数搜索。
'''
    report = ROOT/'docs/mechanism-conditioned-ssl-extend/formal-results.md'
    text = report.read_text(encoding='utf-8')
    heading = '## 结果解释与固定诊断补充'
    if heading in text: text = text.split(heading)[0].rstrip()+'\n'
    text += '\n'+summary+'\n'+result.to_markdown(index=False, floatfmt='.6f')+'\n\n'
    text += ('330个部署/seed/头F1点值及三个原抽样上的24个最终臂bootstrap值，'
             '经独立sklearn实现重算一致，最大误差小于1e−12。'
             '内容级错误台账已补齐，不重造抽样或改五项主比较。\n')
    report.write_text(text, encoding='utf-8')
    manifest = read(OUT/'report-manifest.json'); manifest.update({'result_sha256': sha(report),
        'supplement_sha256': sha(OUT/'supplement-seal.json'), 'independent_score_check': True})
    write(OUT/'report-manifest.json', manifest)
    print(result.to_string(index=False), flush=True)
    print('Supplement and independent scoring checks complete; no retraining', flush=True)


if __name__ == '__main__': main()
