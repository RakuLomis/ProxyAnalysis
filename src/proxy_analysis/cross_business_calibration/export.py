"""Trusted historical-data export. Never imported by fitting workers."""
from .common import *
SOURCE=ROOT/'outputs/conditional-proxy-drift-0916/run-01'

def frames(primitive,C,U):
    result={}
    for name,ids,side in [('C_pre',C,'pre'),('C_post',C,'post'),('U_pre',U,'pre')]:
        result[name]=primitive.loc[primitive.session_id.isin(ids)&primitive.side.eq(side),IDENTITY+NUMERIC].sort_values('session_id').reset_index(drop=True)
    result['labels']=primitive.loc[primitive.session_id.isin(set(C)|set(U))&primitive.side.eq('pre'),['session_id','label_id']].sort_values('session_id').reset_index(drop=True)
    return result

def export():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    cfg=config();old=ROOT/'outputs/paired-calibration-budget-0916/run-01';assert read(old/'completion.json')['status']=='complete'
    captures_path=ROOT/'outputs/content-generalization-20260916/business-01/capture-files.parquet'
    inputs=[SOURCE/(x+'.parquet') for x in ['paired-primitives','outer-folds','cohort','eligible-pairs']]+[old/'completion.json',captures_path,CONFIG,ROOT/'plan/cross-business-calibration-plan-20260928.md',Path(__file__)]
    contract={'inputs':{str(p):sha(p) for p in inputs},'config':cfg,'historical_post_qualification':True}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract
    else:write(OUT/'contract.json',contract)
    primitive=pd.read_parquet(SOURCE/'paired-primitives.parquet');folds=pd.read_parquet(SOURCE/'outer-folds.parquet')
    pairs=pd.read_parquet(SOURCE/'eligible-pairs.parquet');captures=pd.read_parquet(captures_path)
    labels=sorted(primitive.label_id.unique(),key=lambda v:objhash([cfg['role_salt'],v]));groups=[labels[i:i+2] for i in range(0,6,2)]
    write(OUT/'business-groups.json',{'hash_serialization':'json.dumps([salt,label], sort_keys=True) UTF-8 SHA256','groups':groups})
    roles=[];scenarios=[];audit=[]
    for dep in cfg['deployments']:
      for fold in range(5):
        f=folds[(folds.protocol==dep)&(folds.fold==fold)];train=f[f.split=='train'];test=f[f.split=='test']
        assert len(train)==96 and len(test)==24
        ordered={l:sorted(g.content_id.unique(),key=lambda c:objhash([cfg['role_salt'],l,c])) for l,g in train.groupby('label_id')}
        for bg,new in enumerate(groups):
          auxiliary=[l for l in labels if l not in new]
          for t in range(4):
           for s in range(2):
            rotation=2*t+s;chosen=set()
            for j,l in enumerate(auxiliary):
                m=2 if (j+t)%4<2 else 1
                chosen.update(ordered[l][(t+2*s+z)%4] for z in range(m))
            C=train[train.content_id.isin(chosen)];U=train[~train.content_id.isin(chosen)]
            assert len(C)==24 and len(U)==72 and not C.label_id.isin(new).any() and U.label_id.isin(new).sum()==32
            name=f'{dep}-f{fold}-g{bg}-r{rotation}'
            data=frames(primitive,C.session_id,U.session_id)
            poisoned=primitive.copy();mask=(poisoned.side.eq('post')&poisoned.session_id.isin(U.session_id))|poisoned.session_id.isin(test.session_id)
            poisoned.loc[mask,NUMERIC]=np.arange(7)+876543210
            poisoned.loc[poisoned.session_id.isin(test.session_id),'label_id']='forbidden-poison-label'
            for k,v in frames(poisoned,C.session_id,U.session_id).items():pd.testing.assert_frame_equal(v,data[k])
            meta={'scenario':name,'protocol':dep,'fold':fold,'business_group':bg,'rotation':rotation,'new_labels':new,
                'C_sessions':sorted(C.session_id),'U_sessions':sorted(U.session_id),'C_contents':sorted(chosen),'U_contents':sorted(U.content_id.unique()),'C_hash':objhash(sorted(chosen))}
            for kind in ['paired','group']:
                folder=OUT/'bundles'/kind/name;folder.mkdir(parents=True,exist_ok=True)
                if kind=='paired':part=data;manifest=meta.copy()
                else:
                    # No session/repetition/post F or shared row ordering in group fitting inputs.
                    part={'G_pre':data['C_pre'][['content_id']+NUMERIC].sort_values(['content_id']+NUMERIC).reset_index(drop=True),
                        'G_post':data['C_post'][['content_id']+FEATURES].sort_values(['content_id']+FEATURES).reset_index(drop=True),'U_pre':data['U_pre']}
                    manifest={k:meta[k] for k in ['scenario','protocol','fold','business_group','rotation','C_contents','U_contents','C_hash']}
                manifest['files']={}
                for k,v in part.items():
                    path=folder/(k+'.parquet');v.to_parquet(path,index=False);manifest['files'][k]={'filename':path.name,'sha256':sha(path),'rows':len(v)}
                write(folder/'manifest.json',manifest)
                bundle=Bundle(folder,kind)
                for role in ['U_post','H_pre','H_post','H_labels','pair_identity']+(['C_pre','C_post','labels'] if kind=='group' else []):
                    try:bundle.get(role)
                    except PermissionError:pass
                    else:raise AssertionError('Forbidden role allowed')
            for directory,ids,side,columns in [('evaluation',test.session_id,'post',IDENTITY+NUMERIC),('reference',U.session_id,'post',IDENTITY+NUMERIC)]:
                path=OUT/directory/name;path.mkdir(parents=True,exist_ok=True)
                primitive.loc[primitive.session_id.isin(ids)&primitive.side.eq(side),columns].sort_values('session_id').to_parquet(path/('H_post.parquet' if directory=='evaluation' else 'U_post.parquet'),index=False)
            test[['session_id','content_id','label_id']].to_parquet(OUT/'evaluation'/name/'H_labels.parquet',index=False)
            sets={'C':C,'U':U,'H':test}
            for a,b in [('C','U'),('C','H'),('U','H')]:
                assert not set(sets[a].content_id)&set(sets[b].content_id)
                for table_,key in [(pairs,'connection_id'),(captures,'sha256')]:
                    assert not set(table_[table_.session_id.isin(sets[a].session_id)][key])&set(table_[table_.session_id.isin(sets[b].session_id)][key])
            for role,g in sets.items():roles.extend({'scenario':name,'business_group':bg,'rotation':rotation,'role':role,'business_role':'new' if r['label_id'] in new else 'cal',**r} for r in g.to_dict('records'))
            scenarios.append({**meta,'C_pairs':int(pairs.session_id.isin(C.session_id).sum())})
            audit.append({'scenario':name,'poison_unchanged':True,'content_flow_capture_disjoint':True,'group_identifiers_removed':True})
    r=save('roles',roles);save('scenarios',scenarios);save('permission-audit',audit)
    for (_,_,_),g in r[(r.role=='C')&(r.protocol=='SHADOWSOCKS')].groupby(['protocol','fold','business_group']):
        assert g.groupby('content_id').rotation.nunique().eq(3).all()
    for _,g in r.groupby(['fold','business_group','rotation','role']):
        assert set(g[g.protocol=='SHADOWSOCKS'].content_id)==set(g[g.protocol=='VLESS'].content_id)
    write(OUT/'permission-gate.json',{'passed':True,'scenarios':240,'poison_tests':240,'historical_post_qualification':True})
    (DOC/'permissions.md').write_text('# XBC0–XBC2 权限与角色\n\n'+table(pd.DataFrame([{'business_group':i,'new_labels':' / '.join(v)} for i,v in enumerate(groups)]))+'\n\n240个scenario，C=24访问，U=72访问，其中new=32。8轮换全部均衡；C无new业务。双侧历史资格依赖保留；不等于无需捕获U_post。组级worker无校准配对身份，参考臂另包隔离。污染、禁止访问、flow/capture互斥检查通过。\n',encoding='utf-8')
    print('Export passed: 240 scenarios',groups,flush=True)
