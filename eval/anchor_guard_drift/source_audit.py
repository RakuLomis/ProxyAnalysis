"""Only legal source-pre and C observations; no target oracle lookup."""
from common import *
from anchors import arrays,observations,distance
from guard import project,uniform
from affine import apply

def run():
    with stage('source_audit'):
        rows=[];fullrows=[];registries={arm:read(OUT/'rules'/f'{arm}-rules.json') for arm in ['P','G']}
        for ri,r in enumerate(contract()['roles']):
            d=package(rolepath(r)/'source-pre.parquet','source-audit');a=arrays(d)
            coords=artifact(rolepath(r)/'frozen-scaler.pt');mu=coords['mu'];sd=coords['scale']
            payload={'rawpre':a,'mu':mu,'scale':sd}
            for arm in ['P','G']:
                m=artifact(ROOT/r['reuse_maps'][arm]);b0=apply(m,(a-mu)/sd)*sd+mu
                rr=registries[arm][r['id']]['rules'];active=registries[arm][r['id']]['blocks'];z=project(a,b0,rr,active)
                views={arm+'-original':b0,arm+'-Guard':z}
                if arm=='P':views['P-Uniform'],gamma=uniform(a,b0,z);payload['uniform_gamma']=gamma
                for name,v in views.items():
                    payload[name]=(v-mu)/sd;delta=torch.linalg.vector_norm(v-b0,dim=1)
                    sumerr=torch.stack([(v[:,block(j)].sum(1)-1).abs() for j in range(10)],dim=1)
                    rows.append({'role_id':r['id'],'target':r['target'],'group':r['group'],'arm':name,'active_blocks':len(active),
                                 'modified_visits':int((delta>1e-12).sum()),'source_visits':288,'mean_correction':float(delta.mean()),
                                 'max_correction':float(delta.max()),'mean_raw_displacement':float(torch.linalg.vector_norm(v-a,dim=1).mean()),
                                 'negative_coordinate_fraction':float((v<0).double().mean()),'mean_block_mass_error':float(sumerr.mean()),
                                 'max_block_mass_error':float(sumerr.max()),'physical_traffic_qualified':False})
                root=rolepath(r)/'full'
                if arm=='P':
                    p=package(root/'P.parquet','P-fit');ca,cb=arrays(p,True);cm=apply(m,(ca-mu)/sd)*sd+mu
                    ta=p.content_token.to_numpy();aa,bb,_=observations(ca,cb,ta);mm=cm
                else:
                    p=package(root/'G-pre.parquet','G-fit');q=package(root/'G-post.parquet','G-fit')
                    ca=arrays(p);cb=arrays(q);cm=apply(m,(ca-mu)/sd)*sd+mu
                    aa,bb,uu=observations(ca,cb,p.content_token.to_numpy(),q.content_token.to_numpy())
                    mm=torch.cat([cm[np.flatnonzero(p.content_token.to_numpy()==u)].repeat_interleave(4,dim=0) for u in sorted(set(p.content_token))])
                for rule in rr:
                    j=rule['block'];eps=rule['epsilon'];dr=distance(aa[:,block(j)],bb[:,block(j)]);dm=distance(aa[:,block(j)],mm[:,block(j)])
                    fullrows.append({'role_id':r['id'],'target':r['target'],'arm':arm,'feature':FEATURES[j],'block':j,'epsilon':eps,
                                     'training_in_sample_real_violation':float((dr>eps+1e-12).double().mean()),
                                     'training_in_sample_map_violation':float((dm>eps+1e-12).double().mean()),
                                     'used_for_gate':False})
            put(payload,OUT/'source-views'/r['id']/'views.pt',role_id=r['id'],classifier_labels_present=False,target_oracle_used=False,
                adapted_views_not_physical_traffic=True,stage_two_authorized=False)
            if (ri+1)%12==0:progress('frozen_source_view_audit',roles=ri+1,total=60)
        save(pd.DataFrame(rows),OUT/'audits/source-view-change.parquet')
        cols=['role_id','target','arm','feature','block','epsilon','training_in_sample_real_violation','training_in_sample_map_violation','used_for_gate']
        save(pd.DataFrame(fullrows,columns=cols),OUT/'audits/full-C-map-descriptive.parquet')

if __name__=='__main__':run()
