"""CT27-CT34 exhaustive source pseudo-target selection and target post-only inference."""
from common import *

def modelpath(r, arm, t): return OUT/'models'/r['id']/f'{arm}-t{t:g}.pt'
def fit_roles(inner):
    c = start('main_inner_fit' if inner else 'main_outer_fit')
    selected = {} if inner else {(r['outer'], r['target'], r['group'], r['arm']): r['t']
                                 for r in read(OUT/'selection/choices.json') if r['arm'] in ARMS}
    if not inner: require(sha(OUT/'selection/choices.json') == read(OUT/'selection/complete.json')['sha256'], 'Main selection changed')
    count = 0; total = 14400 if inner else 300
    for r in c['main']:
        if (r['inner'] is not None) != inner: continue
        for arm in ARMS:
            slot = artifact(OUT/'slots'/r['id']/(arm+'.pt'))
            for t in TS if inner else [selected[(r['outer'], r['target'], r['group'], arm)]]:
                p = modelpath(r, arm, t)
                if p.with_suffix('.json').exists(): artifact(p)
                else:
                    m, log = fit(slot['x'], slot['y'], slot['mass'], t)
                    save_artifact({'mu': slot['mu'], 'scale': slot['scale'], **m}, p,
                                  optimizer=log, role_id=r['id'], arm=arm, t=t, target_U_read=False)
                count += 1
                if count % 10 == 0:
                    progress('CT27_main_inner_fit' if inner else 'CT31_main_outer_fit', models=count, total=total,
                             role=r['id'], arm=arm, t=t)
    require(count == total, 'Main fit count')
    finish('main_inner_fit' if inner else 'main_outer_fit', fitted_models=count, expected=total)

def inner_predict():
    c = start('main_inner_predict'); rows = []
    for r in c['main']:
        if r['inner'] is None: continue
        q = package(rolepath(r)/'query.parquet', 'main-predict')
        for arm in ARMS:
          for t in TS:
            d = predict(artifact(modelpath(r, arm, t)), q)
            for key in ['outer', 'inner', 'target', 'calibration', 'group']: d[key] = r[key]
            d['arm'] = arm; d['t'] = t; rows.append(d)
    path = OUT/'selection/inner-predictions.parquet'; save(pd.concat(rows, ignore_index=True), path)
    require(sum(len(x) for x in rows) == 345600, 'Main inner prediction count')
    complete(path.parent/'predictions-complete.json', sha256=sha(path), rows=345600, outer_labels_read=False)
    finish('main_inner_predict', rows=345600)

def select():
    c = start('main_select'); path = OUT/'selection/inner-predictions.parquet'
    require(sha(path) == read(path.parent/'predictions-complete.json')['sha256'], 'Inner prediction seal')
    pred = pd.read_parquet(path); labels = []
    for r in c['main']:
        if r['inner'] is None: continue
        d = package(rolepath(r)/'labels.parquet', 'main-select').drop(columns='protocol')
        for key in ['outer', 'inner', 'target', 'calibration', 'group']: d[key] = r[key]
        labels.append(d)
    score = pred.merge(pd.concat(labels, ignore_index=True),
                       on=['outer', 'inner', 'target', 'calibration', 'group', 'visit_id'], validate='many_to_one')
    summaries = []
    for key, d in score.groupby(['outer', 'target', 'group', 'arm', 't']):
        values = []
        for pseudo, part in d.groupby('calibration'):
            require(len(part) == 96 and part.content_id.nunique() == 24 and part.visit_id.is_unique, 'Pseudo-target OOF coverage')
            values.append(metrics(truths(part), part[[f'p{i}' for i in range(6)]].to_numpy(), MASKS[key[2]])[0]['F1_uncovered'])
        require(len(values) == 3, 'Pseudo-target deployment count')
        summaries.append(dict(zip(['outer', 'target', 'group', 'arm', 't'], key), F1=float(np.mean(values))))
    table = pd.DataFrame(summaries); choices = []
    for key, d in table.groupby(['outer', 'target', 'group']):
        base = dict(zip(['outer', 'target', 'group'], key))
        for arm in ARMS:
            a = d[d.arm.eq(arm)]; w = a[a.F1 >= a.F1.max()-1e-12].sort_values('t').iloc[0]
            choices.append({**base, 'arm': arm, 't': float(w.t), 'source_inner_F1': float(w.F1)})
        a = d[d.arm.isin(['CT0', 'CT2'])]
        w = a[a.F1 >= a.F1.max()-1e-12].sort_values(['arm', 't']).iloc[0]
        choices.append({**base, 'arm': 'StrongPost', 'selected_arm': w.arm,
                        't': float(w.t), 'source_inner_F1': float(w.F1)})
    require(len(choices) == 360, 'Selected methods')
    save(table, OUT/'selection/candidates.parquet'); write(OUT/'selection/choices.json', choices)
    complete(OUT/'selection/complete.json', sha256=sha(OUT/'selection/choices.json'), choices=360,
             actual_target_used=False, outer_labels_read=False)
    finish('main_select', choices=360)

def outer_predict():
    c = start('main_outer_predict'); rows = []
    choices = read(OUT/'selection/choices.json')
    require(sha(OUT/'selection/choices.json') == read(OUT/'selection/complete.json')['sha256'], 'Selection seal')
    selected = {(v['outer'], v['target'], v['group'], v['arm']): v for v in choices}
    oldmodels = {(r['outer'], r['protocol']): r for r in read(OUT/'manifests/reused-post-models.json')}
    for r in c['main']:
        if r['inner'] is not None: continue
        q = package(rolepath(r)/'query.parquet', 'main-predict')
        for arm in ARMS+['StrongPost', 'CT5']:
            if arm == 'CT5':
                prior = oldmodels[(r['outer'], r['target'])]; p = ROOT/prior['path']
                checked(p, c['baseline_sha256'], 'extra_resource_reference')
                m = torch.load(p, map_location=device(), weights_only=True); t = prior['t']
            else:
                v = selected[(r['outer'], r['target'], r['group'], arm)]; t = v['t']
                actual_arm = v['selected_arm'] if arm == 'StrongPost' else arm
                m = artifact(modelpath(r, actual_arm, t))
            d = predict(m, q)
            for key in ['outer', 'target', 'group']: d[key] = r[key]
            d['arm'] = arm; d['t'] = t; rows.append(d)
    path = OUT/'predictions/visits.parquet'; save(pd.concat(rows, ignore_index=True), path)
    require(sum(len(x) for x in rows) == 10080, 'Main prediction count')
    complete(path.parent/'complete.json', sha256=sha(path), rows=10080, unique_parent_visits=480,
             outer_labels_read=False, test_pre_read=False, query_schema=['visit_id', *HIST])
    finish('main_outer_predict', rows=10080, post_only=True)

if __name__ == '__main__':
    import sys
    {'inner-fit': lambda: fit_roles(True), 'inner-predict': inner_predict, 'select': select,
     'outer-fit': lambda: fit_roles(False), 'predict': outer_predict}[sys.argv[1]]()
