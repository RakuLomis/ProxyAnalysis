"""Trusted exporter ONLY. Never import this from fitting workers."""
from .common import *
SOURCE=ROOT/'outputs/conditional-proxy-drift-0916/run-01'

def train_frames(primitive,C,U):
    # Select by role and side before assembling any training table.
    result={}
    for name,ids,side in [('C_pre',C,'pre'),('C_post',C,'post'),('U_pre',U,'pre')]:
        result[name]=primitive.loc[primitive.session_id.isin(ids)&primitive.side.eq(side),IDENTITY+NUMERIC].sort_values('session_id').reset_index(drop=True)
    result['labels']=primitive.loc[primitive.session_id.isin(set(C)|set(U))&primitive.side.eq('pre'),['session_id','label_id']].sort_values('session_id').reset_index(drop=True)
    return result

def export():
    OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    assert read(SOURCE/'completion.json')['status']=='complete'
    primitive=pd.read_parquet(SOURCE/'paired-primitives.parquet');folds=pd.read_parquet(SOURCE/'outer-folds.parquet')
    cohort=pd.read_parquet(SOURCE/'cohort.parquet');pairs=pd.read_parquet(SOURCE/'eligible-pairs.parquet')
    assert len(cohort)==240 and len(primitive)==480
    paths=[SOURCE/(x+'.parquet') for x in ['paired-primitives','outer-folds','cohort','eligible-pairs']]+[SOURCE/'completion.json',CONFIG,
        ROOT/'plan/paired-calibration-budget-plan-20260928.md',*Path(__file__).parent.glob('*.py'),ROOT/'eval/paired_calibration_budget/run.py']
    contract={'inputs':{str(p):sha(p) for p in paths},'config':config(),'historical_dual_side_qualification':True,'planned_classifiers':2160}
    if (OUT/'contract.json').exists():assert read(OUT/'contract.json')==contract,'Changed export contract'
    else:write(OUT/'contract.json',contract)
    roles=[];scenarios=[];audits=[];cfg=config()
    for dep in cfg['deployments']:
      for fold in range(5):
        f=folds[(folds.protocol==dep)&(folds.fold==fold)];train=f[f.split=='train'];test=f[f.split=='test']
        assert len(train)==96 and len(test)==24 and not set(train.content_id)&set(test.content_id)
        ordered={label:sorted(g.content_id.unique(),key=lambda c:objhash([cfg['role_salt'],label,c])) for label,g in train.groupby('label_id')}
        assert all(len(v)==4 for v in ordered.values())
        for k in cfg['budgets_per_business']:
          for rotation in cfg['rotations']:
            chosen={v[(rotation+i)%4] for v in ordered.values() for i in range(k)}
            C=train[train.content_id.isin(chosen)];U=train[~train.content_id.isin(chosen)]
            assert len(C)==24*k and len(U)==96-24*k
            assert not set(C.content_id)&set(U.content_id)
            name=f'{dep}-f{fold}-k{k}-r{rotation}';folder=OUT/'bundles'/name;folder.mkdir(parents=True,exist_ok=True)
            data=train_frames(primitive,C.session_id,U.session_id)
            poisoned=primitive.copy()
            forbidden=(poisoned.side.eq('post')&poisoned.session_id.isin(U.session_id))|poisoned.session_id.isin(test.session_id)
            poisoned.loc[forbidden,NUMERIC]=np.arange(7)+987654321
            changed=train_frames(poisoned,C.session_id,U.session_id)
            for key in data:pd.testing.assert_frame_equal(data[key],changed[key])
            files={}
            for key,frame in data.items():
                path=folder/(key+'.parquet');frame.to_parquet(path,index=False)
                files[key]={'filename':path.name,'sha256':sha(path),'rows':len(frame)}
            manifest={'scenario':name,'protocol':dep,'fold':fold,'k':k,'rotation':rotation,'files':files,
                'C_sessions':sorted(C.session_id),'U_sessions':sorted(U.session_id),
                'C_contents':sorted(C.content_id.unique()),'U_contents':sorted(U.content_id.unique()),
                'C_hash':objhash(sorted(C.content_id.unique())),'historical_qualification_used_post':True}
            write(folder/'manifest.json',manifest)
            # Inference and score packages reside outside the training bundle.
            destination=OUT/'evaluation'/name;destination.mkdir(parents=True,exist_ok=True)
            primitive.loc[primitive.side.eq('post')&primitive.session_id.isin(test.session_id),IDENTITY+NUMERIC].sort_values('session_id').to_parquet(destination/'H_post.parquet',index=False)
            test[['session_id','content_id','label_id']].sort_values('session_id').to_parquet(destination/'H_labels.parquet',index=False)
            for role,g in [('C',C),('U',U),('H',test)]:
                roles.extend({'scenario':name,'k':k,'rotation':rotation,'role':role,**r} for r in g.to_dict('records'))
            bundle=TrainingBundle(folder)
            for denied in ['U_post','H_pre','H_post','H_labels','../../paired-primitives']:
                try:bundle.get(denied)
                except PermissionError:pass
                else:raise AssertionError('Forbidden access succeeded')
            paircount=int(pairs.session_id.isin(C.session_id).sum())
            cpost=data['C_post'];scenarios.append({'scenario':name,'protocol':dep,'fold':fold,'k':k,'rotation':rotation,'C_contents':6*k,'C_visits':24*k,'U_visits':96-24*k,'C_pairs':paircount,'C_post_unique_bytes':int(cpost.U_up.sum()+cpost.U_down.sum())})
            audits.append({'scenario':name,'poison_U_post_H_all_input_invariant':True,'forbidden_requests_rejected':True,'content_disjoint':True,'training_bundle_has_post_U':False})
    role=save('roles',roles);s=save('scenarios',scenarios);save('permission-export-audit',audits)
    assert len(s)==120
    for (dep,fold,k,c),g in role[(role.role!='H')].groupby(['protocol','fold','k','content_id']):assert g[g.role=='C'].rotation.nunique()==k
    for (fold,k,r),g in role.groupby(['fold','k','rotation']):
        for what in ['C','U','H']:assert g[(g.role==what)&(g.protocol=='SHADOWSOCKS')].content_id.unique().tolist()==g[(g.role==what)&(g.protocol=='VLESS')].content_id.unique().tolist() or set(g[(g.role==what)&(g.protocol=='SHADOWSOCKS')].content_id)==set(g[(g.role==what)&(g.protocol=='VLESS')].content_id)
    for (dep,fold,r),g in role[role.role=='C'].groupby(['protocol','fold','rotation']):assert set(g[g.k==1].content_id)<set(g[g.k==2].content_id)<set(g[g.k==3].content_id)
    write(OUT/'permission-gate.json',{'passed':True,'scenarios':120,'poisoned_exports_identical':True,'historical_post_dependency_retained':True,'classification_started':False})
    (DOC/'permissions-and-budget.md').write_text('# CB0–CB2 配对预算与权限\n\n120个scenario导出完成：2部署×5折×3预算×4轮换。三个seed共享角色，不改变预算。C/U/H内容互斥；每业务内容循环均衡、预算嵌套，两部署同角色。\n\n'+table(s.groupby(['protocol','k']).agg(scenarios=('scenario','size'),C_contents=('C_contents','first'),C_visits=('C_visits','first'),U_visits=('U_visits','first'),C_pairs_min=('C_pairs','min'),C_pairs_max=('C_pairs','max')).reset_index())+'\n\n训练包只含C_pre/C_post/U_pre/训练Y。全部scenario的U_post及H全部数值污染测试均不改变训练包；禁止字段请求全部被拒绝。H_post与H_Y独立存于evaluation目录。\n\n历史共同连接资格使用过post，当前冻结后不重选；这是既有审计队列上的拟合权限模拟，不是无需采集U_post的证明。导出器为受信数据管理，普通Python允许列表不是OS沙箱。\n',encoding='utf-8')
    print('CB0-CB2: 120 isolated bundles; all role and poisoning checks passed',flush=True)
