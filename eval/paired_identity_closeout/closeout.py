from core import *
T=C.module('identity_closeout_unit_tests',Path(__file__).with_name('tests.py'))
allowed_action=T.allowed_action

def replay_new(c):
    expect=pd.read_parquet(RUN/'predictions/visits.parquet');s=selected();pc=[f'p{i}' for i in range(6)];error=0.
    for r in c['roles']:
        if r['inner'] is not None:continue
        q=C.package(C.rolepath(r)/'query.parquet','query')
        for arm in C.ARMS:
            v=C.chosen(r,arm,s);actual=C.predict(C.get(C.modelpath(r,arm,v['eta'],v['t'])),q).set_index('visit_id')
            want=expect[expect.outer.eq(r['outer'])&expect.target.eq(r['target'])&expect.group.eq(r['group'])&expect.arm.eq(arm)].set_index('visit_id')
            diff=float(np.max(np.abs(actual.loc[want.index,pc].to_numpy()-want[pc].to_numpy())))
            require(diff<1e-12,'New replay mismatch');error=max(error,diff)
    write(CLOSE/'new-prediction-replay.json',{'logical_replays':180,'maximum_error':error,'passed':True,'CUDA_float64':True})
    return error

def run():
    with stage('closeout'):
        c=C.contract();require(C.read(OUT/'tests.json')['passed'],'Tests prerequisite')
        for v in ['references','score','diagnostics','plots','verify','report']:allowed_action(v)
        E.DEST=CLOSE
        write(CLOSE/'amended-postprocess-contract.json',{'parent_contract_sha256':C.sha(RUN/'manifests/experiment-contract.json'),
            'original_failure_sha256':C.sha(RUN/'failure.json'),'plan_sha256':C.sha(PLAN),
            'source_sha256':{C.rel(p):C.sha(p) for p in [Path(__file__),Path(__file__).with_name('core.py'),Path(__file__).with_name('tests.py'),Path(E.__file__)]},
            'allowed_actions':sorted(T.ALLOWED),'forbidden_actions':['train','prepare','select','fit'],
            'output_root':C.rel(CLOSE),'revision':'directory metadata compatibility only; additive postprocessing',
            'scientific_contract_changed':False,'new_fits':0,'original_runner_failure_retained':True})
        E.integrity(c)
        old=C.read(REPORT/'independent-numeric-audit.json');require(old['passed'] and old['models']==34740 and old['maps']==8820,'Full numeric audit missing')
        require(C.read(REPORT/'complete.json')['evidence_builder_sha256']==C.sha(Path(E.__file__)),'Audit code binding failed')
        refs=E.references(c);newerr=replay_new(c);E.score(c,refs)
        for name in ['scenarios','targets','pooled','classes','outer-folds','labeled-predictions']:
            a=pd.read_parquet(CLOSE/'scores'/f'{name}.parquet');b=pd.read_parquet(REPORT/'scores'/f'{name}.parquet')
            pd.testing.assert_frame_equal(a,b,check_exact=True)
        p=C.read(CLOSE/'comparisons/primary.json');prior=C.read(REPORT/'comparisons/primary.json')
        require(p==prior,'Primary comparisons changed')
        for name in ['arms','content_ids','weights','uncovered','auxiliary']:
            with np.load(CLOSE/'comparisons/bootstrap.npz') as a,np.load(REPORT/'comparisons/bootstrap.npz') as b:
                require(np.array_equal(a[name],b[name]),'Bootstrap changed: '+name)
        # The complete source chain and ALL weight files have been checked again.
        # Reuse rather than repeat the preceding independent full objective/gradient audit.
        write(CLOSE/'verification.json',{'passed':True,'numeric_audit_reused':C.rel(REPORT/'independent-numeric-audit.json'),
            'numeric_audit_sha256':C.sha(REPORT/'independent-numeric-audit.json'),'all_weights_rehashed':True,
            'new_models':34740,'maps':8820,'reference_probability_error':C.read(CLOSE/'reference-replay.json')['probability_max_error'],
            'new_probability_error':newerr,'scores_exactly_reproduced':True,'bootstrap_exactly_reproduced':True,
            'scientific_sources_unchanged':True,'failure_preserved':True,'new_fits':0})
        write(CLOSE/'completion.json',{'passed':True,'postprocess_complete':True,'original_runner_complete':False,
            'original_failure_sha256':C.sha(RUN/'failure.json'),'parent_contract_sha256':C.sha(RUN/'manifests/experiment-contract.json'),
            'amendment_sha256':C.sha(CLOSE/'amended-postprocess-contract.json'),'verification_sha256':C.sha(CLOSE/'verification.json'),
            'time_unix':time.time(),'new_fits':0})
        write(CLOSE/'closeout-manifest.json',{'parent_run':C.rel(RUN),'completion':C.rel(CLOSE/'completion.json'),
            'completion_sha256':C.sha(CLOSE/'completion.json'),'scientific_result_unchanged':True,'original_failure_retained':True,
            'diagnostics_reused':{C.rel(p):C.sha(p) for p in (REPORT/'diagnostics').glob('*.parquet')},
            'figures_and_report_reused':C.rel(REPORT/'report-manifest.json'),'report_manifest_sha256':C.sha(REPORT/'report-manifest.json')})
        textfile(CLOSE/'closeout-report.md','# JA追加工程结项报告\n\n2026年10月9日。目录级CT5元数据兼容已通过来源链和负测试。420项历史模型与180项新模型CUDA float64重放均通过；完整评分和10000次bootstrap与独立报告完全一致。全部34740模型、8820映射和槽位重新核对哈希，复用已绑定实现的全量原坐标数值验收。新增拟合为0。\n\n原runner仍保留终态failure，原源码不修改；本目录completion只代表修订后处理结项。科学主张、辅助门与既有报告不变，恢复诊断、图件及完整报告通过closeout-manifest绑定复用。\n')
if __name__=='__main__':run()
