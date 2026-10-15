"""Independent moment gradients and sealed lineage audit; stage two remains blocked."""
from common import *
from anchors import arrays
from affine import group_targets

def verify_map(m,x,y,eta,constant,log):
    n,k=x.shape;mx=x.mean(0);my=y.mean(0);xx=x.T@x/n;yx=y.T@x/n
    tau=max(float(((x-mx).square().sum()/n)/96),1e-12);alpha=eta*tau
    mm=m['matrix'];b=m['bias'];eye=torch.eye(96,device=device(),dtype=torch.float64)
    value=(((x@mm.T+b-y).square().sum()/n)+constant+alpha*(mm-eye).square().sum())/96
    gm=2*(mm@xx+b[:,None]*mx-yx+alpha*(mm-eye))/96;gb=2*(mm@mx+b-my)/96
    grad=max(float(gm.abs().max()),float(gb.abs().max()));err=abs(float(value)-log['objective'])
    require(grad<=1e-8 and err<1e-10,'Independent map objective/gradient rejected')
    return grad,err

def run():
    with stage('verify'):
        for s in ['prepare','tests','diagnostic_predict','score','source_audit','report']:
            require(read(OUT/'stages'/f'{s}.json')['passed'],'Stage incomplete: '+s)
        c=contract()
        for p,h in c['fixed_files'].items():checked(ROOT/p,h,'final-parent-integrity')
        require(not (JA/'completion.json').exists(),'Old failed state overwritten')
        counts=[]
        for r in c['roles']:
            for i in range(4):
                root=rolepath(r)/f'i{i}';dest=OUT/'diagnostics'/r['id']/f'i{i}';coord=artifact(root/'scaler.pt');mu=coord['mu'];sd=coord['scale']
                for arm in ['P','G']:
                    if arm=='P':
                        d=package(root/'P-fit.parquet','P-fit');a,b=arrays(d,True);x=(a-mu)/sd;y=(b-mu)/sd;constant=0.
                    else:
                        p=package(root/'G-pre-fit.parquet','G-fit');q=package(root/'G-post-fit.parquet','G-fit')
                        x=(arrays(p)-mu)/sd;y,constant=group_targets(x,(arrays(q)-mu)/sd,p.content_token.to_numpy(),q.content_token.to_numpy())
                    path=dest/f'{arm}-map.pt';m=artifact(path);log=read(path.with_suffix('.json'))['mapping']
                    counts.append(verify_map(m,x,y,r['eta'],constant,log))
        require(len(counts)==480,'Independent map audit count')
        qualified=pd.read_parquet(OUT/'scores/anchor-qualification.parquet');require(len(qualified)==1200,'Candidate grid')
        require(len(list((OUT/'diagnostics').rglob('*-map.pt')))==480,'Unregistered extra maps')
        gate=read(OUT/'rules/anchor-gate.json')
        files={}
        for p in list(OUT.rglob('*'))+list(DOC.rglob('*')):
            if not p.is_file() or 'plot-cache' in p.parts or p.name in {'progress.json','stage-1-verification.json','completion.json','awaiting-decision.json'}:continue
            require(p.suffix.lower() not in {'.pcap','.pcapng'},'Unexpected capture')
            files[rel(p)]=sha(p)
        history_reads=[]
        for p in (OUT/'ledgers').glob('*.json'):history_reads.extend(read(p)['reads'])
        data_reads=[v for v in history_reads+ACCESS if v['purpose'] not in {'metadata','artifact','sealed-stage-one-code','plan','final-parent-integrity','trusted-map-packer','trusted-view-packer','sealed-C-forecast'}]
        require(not any('/query.parquet' in v['path'] and not v['path'].startswith(rel(OUT)) for v in data_reads),'Historical H query read')
        require(not any('/labels.parquet' in v['path'] for v in data_reads),'H labels read')
        result={'passed':True,'first_stage_complete':True,'new_mapping_fits':480,'new_classifier_fits':0,
                'independent_max_gradient':max(v[0] for v in counts),'independent_max_objective_error':max(v[1] for v in counts),
                'source_files_unchanged':True,'historical_terminal_states_unchanged':True,'files':files,
                'H_query_reads':0,'H_label_reads':0,'target_U_reads':0,'PCAP_reads':0,
                'registered_global_content_split_inherited':True,'physical_post_input_qualified':False,
                'stage_two_authorized':False,'gate':gate}
        write(OUT/'stage-1-verification.json',result)
        write(OUT/'awaiting-decision.json',{'stage_one_complete':True,'status':gate['status'],
               'eligible_for_classification_confirmation':bool(gate['P_anchor_role_blocks']),
               'classification_not_started':True,'threshold_or_method_changes_require_new_registration':True})
        write(OUT/'completion.json',{'passed':True,'first_stage_complete':True,'classification_complete':False,
              'new_mapping_fits':480,'new_classifier_fits':0,'status':gate['status'],'stage_two_authorized':False,
              'verification_sha256':sha(OUT/'stage-1-verification.json'),'physical_post_input_qualified':False})
    progress('stage_one_finished_no_classification',status=gate['status'],P_anchors=gate['P_anchor_role_blocks'])

if __name__=='__main__':run()
