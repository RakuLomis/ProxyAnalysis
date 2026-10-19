"""P0 sealed provenance and train-only preparation, never H tensor unpacking."""
from common import *
from weight_schedule import registry, PRIMARY, REFERENCES

def run():
    with stage('P0'):
        require(not (OUT/'manifests/seal.json').exists(),'Already registered')
        tc=TI/'manifests/experiment-contract.json';sc=SA/'manifests/experiment-contract.json'
        ti=read(tc);sa=read(sc)
        require(sha(tc)==read(tc.with_name('seal.json'))['contract_sha256'],'TI contract seal')
        require(sha(sc)==read(sc.with_name('seal.json'))['contract_sha256'],'SA contract seal')
        for parent in [TI,SA]:
            comp=read(parent/'completion.json');require(comp['passed'],'Historical incomplete')
            require(sha(parent/'verification.json')==comp['verification_sha256'],'Historical verification changed')
        continuation=TI/'manifests/continuation.json'
        require(sha(continuation)==read(continuation.with_name('continuation-seal.json'))['sha256'],'TI continuation seal')
        tv=read(TI/'verification.json');sv=read(SA/'verification.json')
        endpointfile=TI/'manifests/formal-endpoints.parquet';saend=SA/'manifests/new-endpoints.parquet'
        require(sha(endpointfile)==tv['files'][rel(endpointfile)],'TI endpoint lineage')
        saseal=read(SA/'manifests/models-complete.json')
        require(sha(saend)==saseal['endpoints_sha256'] and sha(saend)==sv['files'][rel(saend)],'SA endpoint lineage')
        endpoints=pd.read_parquet(endpointfile);newends=pd.read_parquet(saend)
        roles=ti['roles'];require(len(roles)==60 and all(r['inner'] is None for r in roles),'60 outer roles only')
        require({(r['outer'],r['target'],r['group']) for r in roles}=={(f,p,g) for f in range(5) for p in PROTOCOLS for g in MASKS},'Complete role grid')
        fixed={};arts={};packages={};refs=[];bindings=[];membership=[]
        def fix(p,expected=None):
            h=sha(p);require(expected is None or h==expected,'Historical hash mismatch '+rel(p));fixed[rel(p)]=h
            checked(p,h,'historical-hash-binding');return h
        def art(p,expected=None):
            i=read(p.with_suffix('.json'));h=fix(p,expected);require(h==i['sha256'],'Artifact checksum')
            arts[rel(p)]=h;fix(p.with_suffix('.json'),ti['fixed_files'].get(rel(p.with_suffix('.json')),sa['fixed_files'].get(rel(p.with_suffix('.json')))))
            return i
        for p in [tc,tc.with_name('seal.json'),sc,sc.with_name('seal.json'),continuation,continuation.with_name('continuation-seal.json'),
                  TI/'completion.json',TI/'verification.json',SA/'completion.json',SA/'verification.json',endpointfile,saend,
                  SA/'manifests/models-complete.json',TI/'manifests/numeric-policy.json',V4/'manifests/numeric-policy.json']:
            fix(p)
        oldcode={**ti['historical_source_sha256'],**ti['source_sha256'],**read(continuation)['source_sha256'],**sa['source_sha256']}
        for p,h in oldcode.items():fix(ROOT/p,h)
        for p,h in ti['fixed_files'].items():
            # Bind upstream selections/role contracts, never deserialize historical H scores.
            if '/selection/' in p or ('/manifests/' in p and 'predictions' not in p):fix(ROOT/p,h)
        foldsets={}
        for r in roles:
            rid=r['id'];tr=set(r['train_contents']);h=set(r['validation_contents']);cc=set(r['C_contents']);uu=set(r['U_contents'])
            require(len(tr)==24 and len(h)==6 and not tr&h and cc|uu==tr and not cc&uu,'Content partitions')
            require(len(cc)==16 and len(uu)==8 and r['missing']==MASKS[r['group']],'C/U partition')
            require(r['target']==r['calibration'] and set(r['sources'])==set(PROTOCOLS)-{r['target']},'Deployment permissions')
            require(foldsets.setdefault(r['outer'],h)==h,'Global content folds')
            vp=TI/'slots'/rid/'views.pt';vi=art(vp)
            require(vi['t']==r['t'] and vi['eta']==r['eta'] and not vi['source_sides_row_matched'],'Frozen view provenance')
            for kind,mp in vi['mappings'].items():
                info=art(ROOT/mp,ti['artifacts'].get(mp))
                require(info['mapping']['accepted'],'Unaccepted mapping')
                bindings.append(dict(role_id=rid,kind=kind+'-map',path=mp,sha256=arts[mp],eta=r['eta'],t=r['t']))
            for fn in ['source-post.parquet','source-pre.parquet','C-post.parquet','query.parquet','labels.parquet']:
                path=rolepath(r)/fn;i=ti['packages'][rel(path)];packages[rel(path)]=i
                # Deferred query/labels are bound to upstream seals without opening file bodies.
                if fn not in ['query.parquet','labels.parquet']:fix(path,i['sha256'])
            for name in ['S','P-small','G-small','P-full','G-full','RawPre-small','RawPost-small']:
                if name=='S':
                    p=V4/'models'/rid/f'CT2-t{r["t"]:g}.pt';expected=ti['artifacts'][rel(p)]
                else:
                    e=(endpoints if name[0] in ['P','G'] else newends)
                    z=e[e.role_id.eq(rid)&e.arm.eq(name)];require(len(z)==1,'Historical endpoint uniqueness')
                    p=ROOT/z.iloc[0].model_path;expected=z.iloc[0].model_sha256
                info=art(p,expected);require(info['optimizer']['accepted'] and info['optimizer']['solver']==SOLVER,'Accepted original backend')
                refs.append(dict(role_id=rid,alias=name,path=rel(p),sha256=arts[rel(p)]))
            for name,contents in [('train',tr),('C',cc),('forbidden-U',uu),('H',h)]:
                membership.extend(dict(role_id=rid,scope=name,content_id=u) for u in sorted(contents))
            bindings.append(dict(role_id=rid,kind='views',path=rel(vp),sha256=arts[rel(vp)],eta=r['eta'],t=r['t']))
        require(len(set.union(*foldsets.values()))==30 and sum(map(len,foldsets.values()))==30,'Fold overlap')
        require(len(refs)==420,'Reference count')
        own={rel(p):sha(p) for p in Path(__file__).parent.glob('*.py')}
        require(ast.dump(ast.parse((ROOT/'eval/calibrated_deployment_transfer_v4/optimizer_preconditioning.py').read_text()))==
                ast.dump(ast.parse(Path(__file__).with_name('solver_v4.py').read_text())),'Backend AST differs')
        require(read(V4/'manifests/numeric-policy.json')==POLICY,'Numeric policy changed')
        write(OUT/'manifests/numeric-policy.json',POLICY)
        env=dict(python=sys.executable,torch=str(torch.__version__),numpy=np.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                 installed_LBFGS=inspect.getfile(torch.optim.LBFGS),installed_LBFGS_sha256=sha(Path(inspect.getfile(torch.optim.LBFGS))),device='cuda:0',dtype='float64')
        require(env['installed_LBFGS_sha256']==ti['environment']['installed_LBFGS_sha256'],'Installed optimizer changed')
        proposal=Path('C:/Users/Windows/Desktop/RA1_implementation_plan.md')
        textfile(DOC/'proposal-source.md',proposal.read_text(encoding='utf-8-sig'))
        c=dict(version='RA1-v1',authorized='好的，请你根据计划实施',client_date='2026-10-18',registered_unix=time.time(),
               plan_sha256=sha(PLAN),proposal_sha256=sha(proposal),roles=roles,policies=registry(),primary=PRIMARY,references=REFERENCES,
               artifacts=arts,fixed=fixed,packages=packages,historical_endpoints=refs,code=own,environment=env,
               new_fit_cap=1920,optional_reference_rebuild_cap=420,extra_fit_cap=8,total_attempt_cap=2348,active_budget_seconds=28800,
               actual_target_U_training_reads=0,H_pre_reads=0,selection=False,bootstrap_seed=20261017,bootstrap_samples=10000,family=6)
        write(OUT/'manifests/contract.json',c);write(OUT/'manifests/seal.json',dict(sha256=sha(OUT/'manifests/contract.json')))
        save(pd.DataFrame(bindings),OUT/'manifests/source-bindings.parquet');save(pd.DataFrame(membership),OUT/'manifests/role-membership.parquet')
        write(OUT/'manifests/historical-endpoints.json',refs);write(OUT/'manifests/candidate-registry.json',registry())
        # Only after contract exists may train-only consumers open numeric packages.
        rows=[]
        for r in roles:
            v=artifact(TI/'slots'/r['id']/'views.pt');pre=package(rolepath(r)/'source-pre.parquet','train')
            post=package(rolepath(r)/'source-post.parquet','train');cp=package(rolepath(r)/'C-post.parquet','train')
            require(len(pre)==len(post)==288 and len(cp)==64,'Train shape')
            require(pre.groupby(['protocol','content_id','label_id']).size().eq(4).all(),'Source repeats')
            require(pre.groupby(['protocol','content_id','label_id']).size().equals(post.groupby(['protocol','content_id','label_id']).size()),'Source bags')
            require(torch.equal(v['main_x'],(tensor(post[HIST])-v['mu'])/v['scale']) and torch.equal(v['C_x'],(tensor(cp[HIST])-v['mu'])/v['scale']),'Real post replay')
            require(torch.equal(v['main_y'],tensor(truths(post),torch.long)) and torch.equal(v['C_y'],tensor(truths(cp),torch.long)),'Real labels')
            require(torch.equal(v['P_y'],tensor(truths(pre),torch.long)) and torch.equal(v['P_y'],v['G_y']),'Pre order')
            v['rawpre_x']=(tensor(pre[HIST])-v['mu'])/v['scale']
            for side in ['P','G']:
                mp=read((TI/'slots'/r['id']/'views.pt').with_suffix('.json'))['mappings'][side];m=artifact(ROOT/mp)
                require(torch.equal(m['mu'],v['mu']) and torch.equal(m['scale'],v['scale']),'Map coordinates')
                require(float((v['rawpre_x']@m['matrix'].T+m['bias']-v[side+'_x']).abs().max())<1e-12,'Map replay')
            put(trainpath(r),v,role_id=r['id'],capability='train-only',source_views_sha256=sha(TI/'slots'/r['id']/'views.pt'))
            led=[]
            for name,d in [('source-post',post),('CORAL',post),('P',pre),('G',pre),('RawPre',pre),('RawPost',post),('C-post',cp)]:
                for j,item in enumerate(d.itertuples()):led.append(dict(role_id=r['id'],input_view=name,row_index=j,label_id=item.label_id,content_key=item.content_id,
                  parent_visit_key=getattr(item,'visit_id',None),anonymous_pre_row=j if name in ['P','G','RawPre'] else None))
            save(pd.DataFrame(led),OUT/'packages'/r['id']/'row-provenance.parquet')
            rows.append(dict(role_id=r['id'],training_visits=352,source=288,C=64,source_row_matched=False,H_reads=0,U_reads=0))
        save(pd.DataFrame(rows),OUT/'audits/P0-audit.parquet')
        write(OUT/'audits/P0-complete.json',dict(roles=60,paired_map_replays=60,group_map_replays=60,reference_bindings=420,new_maps=0,new_scales=0,H_reads=0,U_reads=0))
