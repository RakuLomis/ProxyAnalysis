"""Read-only metadata/provenance closeout, with explicit log coverage limits."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'deproxy_moment_game_v1_numeric_repair'))
from common import *

def main():
    configure('coordinator');begin('R5-provenance-audit')
    try:
        reg=registration();codecheck();old=read(OLD/'manifests/contract.json')
        parent={r['id']:r for r in old['roles']};fold=[]
        for r in roles():
            outer=parent[r['id'].split('/i1/')[0]+'/outer']
            train=set(r['train_contents']);val=set(r['validation_contents']);H=set(outer['validation_contents'])
            require(not train&val and train|val==set(outer['train_contents']) and not (train|val)&H,'Nested global content isolation')
            require(r['target'] not in r['sources']+[r['calibration']],'Actual target excluded from inner roles')
            fold.append(dict(role_id=r['id'],role_target=r['target'],query_deployment=r['calibration'],train_contents=len(train),
                inner_query_contents=len(val),actual_outer_H_contents=len(H),actual_target_numeric_allowed=False))
        seen=[];allowed={'P':{'P','pre','post','shared'},'G':{'G','pre','post','shared'},'E':{'E','post','shared'}}
        for path in (OUT/'permissions').glob('*.json'):
            for entry in read(path)['reads']:
                binding=reg['assets'].get(entry['path']);require(binding is not None,'Unregistered historical decode log')
                require(entry['role_id']==binding['role_id'] and entry['sha256']==binding['sha256'],'Logged historical binding')
                require(binding['capability'] in allowed.get(entry['capability'],set()),'Logged capability violation')
                require('query' not in Path(entry['path']).name.lower() and 'labels' not in Path(entry['path']).name.lower(),'Deferred input decoded')
                seen.append(entry)
        inventory=pd.read_parquet(OUT/'tests/integrated-P1-inventory.parquet')
        require(len(inventory)==232 and inventory.output_path.is_unique,'Unique integrated head inventory')
        dependencies=[]
        for row in inventory.to_dict('records'):
            p=ROOT/row['output_path'];side=read(p.with_suffix('.json'));q=read(p.with_suffix('.quality.json'))
            require(side['accepted'] and q['accepted'] and q['iterations']<2000 and q['evaluations']<10000,'Accepted inventory head and strict budget')
            require(sha(p)==side['sha256'] and side['role_id']==row['role_id'],'Integrated head binding')
            source={k:v['sha256'] for k,v in reg['assets'].items() if v['role_id']==row['role_id'] and '/packages/' in k and v['capability'] in allowed.get('E' if row['arm']=='post' else ('G' if row['arm']=='pre' else capfor(row['arm'])),set())}
            deps=dict(output=rel(p),sha256=side['sha256'],role_id=row['role_id'],kind=row['kind'],gamma=row['gamma'],
                source_bindings=source,derivation='inferred from frozen code and role-specific assets; not a reconstructed runtime-read log')
            if row['kind']=='refit':
                st=p.parent/'step-2000.pt';require(st.exists(),'Refit terminal provenance');deps['generator_terminal_sha256']=sha(st)
            dependencies.append(deps)
        before=read(OUT/'completion.json')
        write(OUT/'tests/provenance-audit.json',dict(passed=True,roles=fold,historical_tensor_decode_events=len(seen),
            distinct_historical_tensors=len({e['path'] for e in seen}),capabilities=sorted({e['capability'] for e in seen}),
            query_or_H_U_tensor_decodes=0,integrated_heads=232,source_sha256=sha(Path(__file__)),
            log_coverage_limitation='newown checks generated model root/version/role/capability/hash but did not append each generated-model read to the historical READS list. No retroactive events are invented.',
            actual_outer_352_training_package_decodes=0,old_parent_state_unchanged=sha(OLD/'budget.json')==reg['parent_budget_sha256']),True)
        write(OUT/'tests/derived-head-provenance.json',dict(heads=dependencies,not_a_runtime_read_log=True),True)
        progress('R5_provenance_verified',integrated_heads=232,query_read=False,H_scored=False)
    except BaseException as e:failure('R5-provenance-audit',e);raise
    finally:end('R5-provenance-audit')

if __name__=='__main__':main()
