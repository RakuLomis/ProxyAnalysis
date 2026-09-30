"""0914 14-class post-only recognition; whole-visit repeat holdouts."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pyarrow
import torch
import yaml
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score,balanced_accuracy_score,confusion_matrix,precision_recall_fscore_support

from .mechanism_contract import read
from .paired_structure_contract import seal,validate_complete
from .business_representations import vector,dictionary
from .natural_pair_ssl import networks,supervised
from .natural_pair_ssl_report import mlp,softmax
from ..paired_information.prepare import table,digest
from ..reproducibility.preflight import write_json,write_table
from ..reproducibility.extract import describe
from ..config import FeatureConfig
from ..indexing.pairs import build_exclusive_pairs
from ..pipeline.analyze_entity import analyze_entity_capture
from ..parsing import PcapNgReader

CONFIG=Path('configs/business-recognition-0914.yaml')
ACTIVITIES={'arxiv.org':'paper_abstract_view','bing.com':'search_results_view','cloudflare.com':'homepage_view',
 'developer.mozilla.org':'document_view','example.com':'static_control_view','github.com':'repository_view',
 'openstreetmap.org':'map_view','rottentomatoes.com':'movie_info_view','tradingview.com':'chart_view',
 'unsplash.com':'image_feed_view','vimeo.com':'video_info_view','weather.com':'weather_view',
 'wikipedia.org':'article_view','youtube.com':'video_playback'}


def settings(config=CONFIG):
    cfg=yaml.safe_load(Path(config).read_text(encoding='utf-8'))
    return cfg,Path(cfg['source_root']),Path(cfg['identity_root']),Path(cfg['output_root'])


def split_ids(rows,fold):
    train=[r for r in rows if r['repetition']!=fold];test=[r for r in rows if r['repetition']==fold]
    if {r['session_id'] for r in train}&{r['session_id'] for r in test}:raise ValueError('Visit overlap')
    if set(r['label_id'] for r in train)!=set(r['label_id'] for r in test):raise ValueError('Missing class')
    return train,test


def clipped_groups(groups,seconds):
    start=min(p.timestamp_ns for g in groups for p in g)
    end=start+round(seconds*1e9)
    return [[p for p in g if start<=p.timestamp_ns<end] for g in groups],start,end


def prepare(config=CONFIG):
    cfg,source,identity,root=settings(config)
    if (root/'prepared/complete.json').exists():verify(config);return
    records=table(source/'cohort.parquet');labels={r['session_id']:r for r in table(source/'labels.parquet')}
    execution={r['session_id']:r for r in table(source/'execution-diagnostics/session-execution.parquet')}
    old={r['session_id']:r for r in table(source/'side-summaries.parquet') if r['scope']=='exclusive_page' and r['selection']=='observed'}
    caps=table(identity/'primary-capture-identities.parquet');proof=read(identity/'result.json')
    if len(records)!=140 or len(caps)!=3422 or proof['audit_errors'] or proof['cross_session_duplicate_file_groups']:
        raise ValueError('Historical identity gate differs')
    comparisons=read(identity/'tuple-reuse-comparisons.json')
    if any(r['time_overlap'] or r['identical_packet_count'] or r['shared_initial_syn_identity_count'] or not r['both_start_initial_syn'] for r in comparisons):
        raise ValueError('Connection identity ambiguous')
    sources=[Path(config),Path(cfg['feature_config'])]+list(Path('src/proxy_analysis').rglob('*.py'))
    sources += [source/n for n in ['cohort.parquet','labels.parquet','side-summaries.parquet','execution-diagnostics/session-execution.parquet']]
    sources += list(identity.glob('*.json'))+[identity/'primary-capture-identities.parquet']
    frozen={str(p):digest(p) for p in sources}
    existing=root/'preparation-contract.json'
    if existing.exists():
        if read(existing)['sources']!=frozen:raise ValueError('Preparation inputs changed')
    else:write_json(existing,{'sources':frozen,'config':cfg})
    fc=FeatureConfig.load(cfg['feature_config']);rows=[];windows=[]
    for i,r in enumerate(sorted(records,key=lambda r:r['session_id'])):
        sid=r['session_id'];domain=r['target_domain'];cache=root/'sessions'/f'{sid}.json'
        if cache.exists():
            value=read(cache)
        else:
            path=Path(r['session_path']);pairs=build_exclusive_pairs(path,r['protocol'])
            counts=Counter((p.post.entity_id,str(p.post.capture_path)) for p in pairs)
            pairs=[p for p in pairs if counts[p.post.entity_id,str(p.post.capture_path)]==1 and p.pre.transport_protocol==p.post.transport_protocol=='tcp']
            selected={str(d.capture_path) for p in pairs for d in [p.pre,p.post]}
            expected={a['path']:a['sha256'] for a in caps if a['session_id']==sid}
            if selected!=set(expected):raise ValueError('Capture selection differs')
            for p,h in expected.items():
                if digest(Path(p))!=h:raise ValueError('Raw capture changed')
            value={'full':{},'prefix8':{},'coverage':[],'sources':expected}
            for side,rawfile in [('pre','tun.pcap'),('post','phys.pcap')]:
                groups=[]
                for pair in pairs:
                    a=analyze_entity_capture(getattr(pair,side))
                    if a.unknown_direction_count:raise ValueError('Unknown packet direction')
                    groups.append(list(a.packet_measures))
                full=describe(groups,fc)
                if not np.allclose(vector(full,'distribution157'),vector(old[sid][side],'distribution157'),equal_nan=True,atol=1e-10,rtol=1e-10):
                    raise ValueError('Full summary replay differs')
                clipped,start,end=clipped_groups(groups,cfg['prefix_seconds'])
                last=max(p.timestamp_ns for g in groups for p in g)
                evidence='selected_capture_packet_after_window'
                if last<end:
                    # Quiet target flows alone cannot certify continued capture.
                    raw=path/'raw'/rawfile
                    if raw.exists():
                        last=max((p.timestamp_ns for p in PcapNgReader(raw)),default=0)
                        value['sources'][str(raw)]=digest(raw)
                        evidence='global_capture_packet_after_window'
                    else:evidence='global_capture_missing'
                value['full'][side]=full;value['prefix8'][side]=describe(clipped,fc)
                value['coverage'].append({'session_id':sid,'domain':domain,'side':side,'anchor_ns':start,
                    'required_end_ns':end,'last_evidence_ns':last,'passed':last>=end,'evidence':evidence,
                    'full_packets':full['packet_count'],'prefix_packets':value['prefix8'][side]['packet_count']})
            write_json(cache,value)
        windows.extend(value['coverage'])
        row={'session_id':sid,'domain':domain,'content_id':r['target_url'],'label_id':domain+'::'+ACTIVITIES[domain],
            'old_label_id':labels[sid]['effective_label_id'],'protocol':r['protocol'],'repetition':r['repetition'],
            'configured_seconds':execution[sid]['configured_duration_seconds'],'started_at':r['started_at'],
            'full_x':vector(value['full']['post'],'distribution157').tolist(),
            'prefix8_x':vector(value['prefix8']['post'],'distribution157').tolist(),
            'observable_size_x':[(value['full']['post']['last_ns']-value['full']['post']['first_ns'])/1e9,
                                 value['full']['post']['packet_count'],value['full']['post']['transport_bytes']]}
        rows.append(row)
        print(f'prepared {i+1}/140 {domain}',flush=True)
    cells=Counter((r['label_id'],r['protocol'],r['repetition']) for r in rows)
    if len(cells)!=140 or set(cells.values())!={1} or len({r['label_id'] for r in rows})!=14:raise ValueError('Incomplete design')
    splits=[]
    for fold in range(1,6):
        tr,te=split_ids(rows,fold);a={r['session_id'] for r in tr};b={r['session_id'] for r in te}
        for key in ['canonical_path','sha256']:
            if {r[key] for r in caps if r['session_id'] in a}&{r[key] for r in caps if r['session_id'] in b}:raise ValueError('Raw identity crosses split')
        splits.append({'fold':fold,'train_ids':sorted(a),'test_ids':sorted(b),'capture_overlap':0})
    write_table(root/'prepared/visits.parquet',rows);write_table(root/'prepared/window-coverage.parquet',windows)
    write_json(root/'prepared/splits.json',splits);write_json(root/'prepared/labels.json',ACTIVITIES)
    passed=all(r['passed'] for r in windows)
    write_json(root/'prepared/gate.json',{'full_passed':True,'prefix8_passed':passed,'failed_side_windows':sum(not r['passed'] for r in windows),
        'scope':cfg['observation_scope'],'whole_flow_disjoint':True,'labels':14,'visits':140,'selection':'observed_exclusive_page',
        'allowed_views':['full','prefix8'] if passed else ['full'],'window_rule':'side_first_packet <= t < side_first_packet+8sec'})
    seal(root/'prepared',passed=True)
    all_sources={**frozen,**{str(p):digest(p) for p in (root/'sessions').glob('*.json')}}
    write_json(root/'contract/manifest.json',{'config':cfg,'sources':all_sources,'features':dictionary(),
        'prepared_sha256':digest(root/'prepared/complete.json'),'raw_hashes_verified_during_extraction':True})
    seal(root/'contract',passed=True)
    print(f'Prepared: prefix8 gate {passed}',flush=True)


def verify(config=CONFIG):
    cfg,source,identity,root=settings(config);validate_complete(root/'contract');m=read(root/'contract/manifest.json')
    if m['config']!=cfg:raise ValueError('Changed config')
    for p,h in m['sources'].items():
        if digest(Path(p))!=h:raise ValueError(f'Changed input {p}')
    validate_complete(root/'prepared')
    if digest(root/'prepared/complete.json')!=m['prepared_sha256']:raise ValueError('Prepared seal changed')
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    return cfg,root


def raw_matrix(rows,view):
    if view=='configured_duration':return np.asarray([[r['configured_seconds']] for r in rows],float)
    return np.asarray([r[view+'_x'] for r in rows],float)


def run(config=CONFIG):
    cfg,root=verify(config);rows=table(root/'prepared/visits.parquet');labels=sorted({r['label_id'] for r in rows})
    views=read(root/'prepared/gate.json')['allowed_views']+['configured_duration','observable_size']
    for view in views:
        for fold in range(1,6):
            tr,te=split_ids(rows,fold);y=[labels.index(r['label_id']) for r in tr]
            imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(raw_matrix(tr,view))
            sc=StandardScaler().fit(imp.transform(raw_matrix(tr,view)))
            x=sc.transform(imp.transform(raw_matrix(tr,view)));xt=sc.transform(imp.transform(raw_matrix(te,view)))
            recipes=[('linear',0)]+([('mlp',s) for s in cfg['seeds']] if view in ['full','prefix8'] else [])
            for model,seed in recipes:
                job=root/'jobs'/f'{view}-{fold}-{model}-{seed}'
                if (job/'complete.json').exists():validate_complete(job);continue
                if model=='linear':
                    fit=LogisticRegression(C=cfg['linear_C'],max_iter=cfg['linear_max_iter'],tol=cfg['linear_tol']).fit(x,y)
                    if max(fit.n_iter_)>=cfg['linear_max_iter']:raise ValueError('Linear convergence')
                    p=fit.predict_proba(xt);state={'coef':fit.coef_.tolist(),'intercept':fit.intercept_.tolist(),'classes':fit.classes_.tolist()}
                else:
                    enc,_=networks(seed);fit,state,trace=supervised(enc,x,y,14,seed,cfg)
                    with torch.no_grad():p=torch.softmax(fit(torch.tensor(xt,dtype=torch.float64)),1).numpy()
                    write_table(job/'trajectory.parquet',trace)
                write_json(job/'fit.json',{'view':view,'fold':fold,'model':model,'seed':seed,'labels':labels,
                    'train_ids':[r['session_id'] for r in tr],'test_ids':[r['session_id'] for r in te],
                    'preprocessing':{'median':imp.statistics_.tolist(),'mean':sc.mean_.tolist(),'scale':sc.scale_.tolist()},'state':state})
                write_table(job/'predictions.parquet',[{k:r[k] for k in ['session_id','label_id','protocol','repetition']}|
                    {'probabilities':prob.tolist(),'view':view,'model':model,'seed':seed,'fold':fold} for r,prob in zip(te,p)])
                seal(job,passed=True);print('trained '+job.name,flush=True)


def scores(rr,labels):
    p=np.asarray([r['probabilities'] for r in rr]);y=np.asarray([labels.index(r['label_id']) for r in rr]);pred=p.argmax(1)
    return {'macro_f1':float(f1_score(y,pred,labels=range(len(labels)),average='macro',zero_division=0)),
        'balanced_accuracy':float(balanced_accuracy_score(y,pred)),
        'ce_bits':float(-np.log2(np.maximum(p[np.arange(len(y)),y],1e-15)).mean()),
        'brier':float(((p-np.eye(len(labels))[y])**2).sum(1).mean()),'visits':len(rr)}


def report(config=CONFIG):
    cfg,root=verify(config);rows=table(root/'prepared/visits.parquet');lookup={r['session_id']:r for r in rows}
    labels=sorted({r['label_id'] for r in rows});predictions=[];max_error=0
    jobs=list((root/'jobs').iterdir());expected=20*len(read(root/'prepared/gate.json')['allowed_views'])+10
    if len(jobs)!=expected:raise ValueError('Incomplete budget')
    for job in jobs:
        validate_complete(job);f=read(job/'fit.json');s=f['preprocessing'];st=f['state']
        tr,te=split_ids(rows,f['fold'])
        if f['train_ids']!=[r['session_id'] for r in tr] or f['test_ids']!=[r['session_id'] for r in te]:raise ValueError('Wrong membership')
        imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(raw_matrix(tr,f['view']))
        sc=StandardScaler().fit(imp.transform(raw_matrix(tr,f['view'])))
        for a,b in [(imp.statistics_,s['median']),(sc.mean_,s['mean']),(sc.scale_,s['scale'])]:
            if not np.allclose(a,b,rtol=0,atol=1e-12):raise ValueError('Train-only preprocessing differs')
        raw=raw_matrix(te,f['view']);x=(np.where(np.isnan(raw),s['median'],raw)-s['mean'])/s['scale']
        if f['model']=='linear':p=softmax(x@np.asarray(st['coef']).T+st['intercept'])
        else:
            h=mlp(x,st['final'],'0.');p=softmax(h@np.asarray(st['final']['1.weight']).T+st['final']['1.bias'])
        rr=table(job/'predictions.parquet')
        if [r['session_id'] for r in rr]!=f['test_ids']:raise ValueError('Prediction order')
        max_error=max(max_error,float(abs(p-np.asarray([r['probabilities'] for r in rr])).max()));predictions.extend(rr)
    if max_error>1e-10:raise ValueError('Independent replay failed')
    groups=defaultdict(list)
    for r in predictions:
        for protocol in [r['protocol'],'pooled']:groups[r['view'],r['model'],r['seed'],protocol].append(r)
    results=[];perclass=[];matrices=[];foldmetrics=[]
    for key,rr in sorted(groups.items()):
        view,model,seed,protocol=key;meta=dict(view=view,model=model,seed=seed,protocol=protocol)
        if len({r['session_id'] for r in rr})!=len(rr):raise ValueError('Repeated test visit')
        results.append({**meta,**scores(rr,labels)})
        y=[labels.index(r['label_id']) for r in rr];yp=[int(np.argmax(r['probabilities'])) for r in rr]
        cm=confusion_matrix(y,yp,labels=range(14));pr,re,f1,support=precision_recall_fscore_support(y,yp,labels=range(14),zero_division=0)
        matrices.append({**meta,'labels':labels,'matrix':cm.tolist()})
        perclass.extend({**meta,'label':lab,'precision':float(pr[i]),'recall':float(re[i]),'f1':float(f1[i]),'support':int(support[i])} for i,lab in enumerate(labels))
        for fold in range(1,6):foldmetrics.append({**meta,'fold':fold,**scores([r for r in rr if r['fold']==fold],labels)})
    out=root/'report';write_table(out/'predictions.parquet',predictions);write_json(out/'metrics.json',results)
    write_json(out/'per-class.json',perclass);write_json(out/'confusion-matrices.json',matrices);write_json(out/'fold-metrics.json',foldmetrics)
    write_json(out/'validation.json',{'passed':True,'fits':len(jobs),'predictions':len(predictions),'max_probability_error':max_error,
        'training_preprocessing_rebuilt':True,'scope':cfg['scenario'],'no_validation_or_early_stopping':True,
        'uniform_reference':{'macro_f1_random_expectation_not_exact':1/14,'ce_bits':float(np.log2(14)),'brier':13/14}})
    seal(out,passed=True)
    for r in results:
        if r['protocol']=='pooled':print(r,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(CONFIG));p.add_argument('--mode',choices=['prepare','run','report'],required=True)
    args=p.parse_args();globals()[args.mode](args.config)
