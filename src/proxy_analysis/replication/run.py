"""Explicit stage execution with logs, selected identities and fail-fast checkpoints."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import pyarrow.parquet as pq
import yaml

from ..information_validation.data import digest
from ..reproducibility.preflight import write_json


def execute(root, name, module, arguments):
    folder = root/'execution'; folder.mkdir(exist_ok=True)
    # Preserve previous failures and commands on reruns.
    if (folder/(name+'.json')).exists() or (folder/(name+'.log')).exists():
        archive = folder/'history'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
        archive.mkdir(parents=True)
        for suffix in ['.json', '.log']:
            previous = folder/(name+suffix)
            if previous.exists(): previous.rename(archive/previous.name)
    command = [sys.executable, '-X', 'utf8', '-m', module, *map(str, arguments)]
    state = {'command': command, 'started': datetime.now(timezone.utc).isoformat(), 'state': 'running',
             'source_sha256': {str(p): digest(p) for p in Path('src/proxy_analysis').rglob('*.py')}}
    write_json(folder/(name+'.json'), state)
    print(name, 'started', flush=True)
    with (folder/(name+'.log')).open('w', encoding='utf-8') as log:
        done = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
    state.update(state='complete' if done.returncode == 0 else 'failed', exit_code=done.returncode,
                 completed=datetime.now(timezone.utc).isoformat())
    write_json(folder/(name+'.json'), state)
    print(name, state['state'], flush=True)
    if done.returncode:
        raise RuntimeError(f'{name} failed; see {folder/(name+".log")}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path('configs/replication-20260914.yaml'))
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--batch',choices=['broad','repeat'],required=True)
    p.add_argument('--stage',choices=['indexes','gates','smoke','features','aligned','broad-analysis','broad-models','repeat-analysis','information'],required=True)
    args=p.parse_args(); root=args.output_root
    if not (root/'provenance.json').is_file(): raise ValueError('run metadata contract first')
    cfg=yaml.safe_load(args.config.read_text(encoding='utf-8'))
    raw=Path(cfg['bundle_root'])/cfg['batches'][args.batch]['directory']
    out=root/args.batch; audit=out/'audit'; stage=args.stage
    run=lambda name,module,argv: execute(root,args.batch+'-'+name,module,argv)
    cli=lambda name,*argv: run(name,'proxy_analysis.cli',list(argv))
    if stage=='indexes':
        cli('index-audit','index-audit',raw,'--output',audit/'index-audit.json')
        return
    if stage=='gates':
        run('scope-gate','proxy_analysis.reproducibility.scope_gate',[audit])
        run('routes','proxy_analysis.reproducibility.metadata_report',[audit])
        return
    if stage in ['smoke','features']:
        rows=pq.read_table(audit/'run_registry.parquet').to_pylist()
        selected=[r for r in rows if r['is_final']]
        if stage=='smoke':
            chosen={}
            for r in selected:
                chosen.setdefault((r['protocol'],'basic'),r)
                if r['target_domain']=='youtube.com' and 'watch?' in r['target_url']:
                    chosen.setdefault((r['protocol'],'playback'),r)
                if r['target_domain']=='zhihu.com':
                    chosen.setdefault((r['protocol'],'degraded_fixture'),r)
                if r['is_first_attempt'] and r['selected_attempt']==1 and sum(x['run_id']==r['run_id'] for x in rows)>1:
                    chosen[(r['session_id'],'retained_retry')]=r
            selected=list({r['session_id']:r for r in chosen.values()}.values())
        feature=out/('smoke-features' if stage=='smoke' else 'features')
        argv=['run-dataset',raw,feature,'--config',cfg['feature_config']]
        for r in selected: argv+=['--session-id',r['session_id']]
        cli(stage+'-extract',*argv)
        quality_args=['quality-report',feature,'--output',out/(stage+'-quality.json')]
        for r in selected: quality_args+=['--session-id',r['session_id']]
        cli(stage+'-quality',*quality_args)
        if stage=='features':
            cli('export','export-ml',feature,out/'ml')
            cli('validate-ml','validate-ml',out/'ml')
            cli('dual-track','build-dual-track',out/'ml',out/'experiments')
        return
    if stage=='aligned':
        aligned=out/'aligned'; aligned.mkdir(exist_ok=True)
        index=aligned/'url-connection-index.parquet'
        cli('url-index','build-url-index',raw,index,'--registry',audit/'run_registry.parquet')
        cli('url-pairs','build-url-pairs',index,out/'ml',out/'experiments',aligned/'url-aligned-pair-features.parquet')
        cli('page-table','build-page-protocol',index,out/'ml',aligned/'page-aligned-protocol-features.parquet')
        cli('aligned-validation','validate-aligned',aligned,'--registry',audit/'run_registry.parquet')
        return
    if stage in ['broad-analysis','broad-models']:
        if args.batch!='broad': raise ValueError('single-visit inference only on broad')
        stats=out/'statistics'; common=['--config',cfg['statistics_config']]
        if stage=='broad-analysis':
            cli('marts','build-statistical-marts',out/'aligned',stats,*common)
            for command in ['run-page-statistics','run-resource-statistics','run-statistical-sensitivity']:
                cli(command,command,stats/'marts',stats,*common)
        approval=['--interpretation-addendum',cfg['interpretation_addendum']] if cfg.get('interpretation_addendum') else []
        cli('statistics-report','finalize-statistics',stats,*common,*approval)
        cli('transformations','analyze-transformations',out/'experiments'/'transformation-common.parquet',
            out/'transformation-statistics.json')
        cli('exploratory-baselines','run-protocol-baselines',out/'experiments',out/'baselines')
        cli('formal','evaluate-tabular',out/'experiments',out/'formal',
            '--outer-splits','5','--outer-repeats','5','--inner-splits','4')
        return
    if stage=='repeat-analysis':
        if args.batch!='repeat': raise ValueError('repeated inference only on repeat')
        for name,argv in [('extract',[audit,'--feature-config',cfg['feature_config'],'--spec',cfg['repeat_spec'],'--selected-only']),
                          ('statistics',[audit,'--config',cfg['repeat_spec']]),('workload_sensitivity',[audit]),('report',[audit])]:
            run('repeat-'+name,'proxy_analysis.reproducibility.'+name,argv)
        return
    if stage=='information':
        if args.batch!='repeat': raise ValueError('repeat information only on repeat')
        run('information','proxy_analysis.information_validation',['--input-root',audit,'--output-root',out/'information-validation',
            '--target-contract',audit/'target-contract.json','--spec',cfg['repeat_spec'],'--config',cfg['information_config']])


if __name__=='__main__': main()
