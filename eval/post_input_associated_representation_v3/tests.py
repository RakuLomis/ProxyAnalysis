"""CUDA unit tests of the model, group loss and scoped IO."""
from common import *
from models import Heads,latent,logits

def run():
    with stage('P1_tests'):
        r=contract()['inner_roles'][0];s=own(taskpath(r)/'classification.pt','test')
        m=own(PARENT/'base-models'/r['id']/'P-small.pt','test');x=s['x'];z=base_logits(m,x)
        h=Heads([20261014]);znew=h(x.float()[None],z[None])[0]
        checks={}
        for name,f in [('logits',lambda a:a),('logprob',lambda a:F.log_softmax(a,1)),('probability',lambda a:torch.softmax(a,1)),('decision',lambda a:a.argmax(1))]:
            checks['zero_'+name]=torch.equal(f(znew),f(z))
        require(all(checks.values()),'Zero initialization gate')
        require(sum(p.numel() for p in h.parameters())==2318,'Residual capacity')
        require(sum(p.numel() for p in Heads([20261014],True).parameters())==1742,'Teacher capacity')
        yy=s['y'];value=(F.cross_entropy(znew,yy,reduction='none')*s['mass']).sum();value.backward()
        checks['CE_head_gradient_positive']=bool(h.get(0,'w2').grad.abs().max()>0)
        checks['CE_G_gradient_zero_at_origin']=bool(h.get(0,'w0').grad.abs().max()==0 and h.get(0,'w1').grad.abs().max()==0)
        g=torch.Generator(device=device()).manual_seed(71);u=torch.randn((3,8),generator=g,device=device(),dtype=torch.float64)
        t=torch.randn((4,8),generator=g,device=device(),dtype=torch.float64)
        left=(u[:,None]-t[None]).square().mean(1);right=(u-t.mean(0)).square()+(t-t.mean(0)).square().mean(0)
        checks['Cartesian_center_squared_identity']=bool(torch.allclose(left,right,rtol=1e-12,atol=1e-12))
        checks['group_permutation_invariant']=bool(torch.allclose(t.mean(0),t[torch.tensor([2,0,3,1],device=device())].mean(0),rtol=1e-12,atol=1e-12))
        negatives=[]
        for p,arm in [(taskpath(r)/'teacher/fit.pt','A3'),(OUT/'targets'/r['id']/'A3.pt','A2'),(OUT/'targets'/r['id']/'A2.pt','A1')]:
            try:own(p,'branch',arm)
            except RuntimeError:negatives.append(True)
            else:negatives.append(False)
        checks['permission_negatives']=all(negatives)
        # Strengthen parent lineage against the completed run's global verification,
        # rather than accepting a changed asset and changed sidecar together.
        parent_done=read(FORMAL/'completion.json');verpath=FORMAL/'verification.json'
        require(parent_done['passed'] and sha(verpath)==parent_done['verification_sha256'],'Parent completion verification seal')
        verified=read(verpath)['files'];parent_contract=read(FORMAL/'manifests/experiment-contract.json');lineage=0
        require(verified[rel(FORMAL/'manifests/experiment-contract.json')]==sha(FORMAL/'manifests/experiment-contract.json'),'Parent registry verification binding')
        for rr in contract()['inner_roles']+contract()['roles']:
            for key in ['old_task','base_path']:
                path=rr[key]
                expected=verified.get(path,parent_contract['artifacts'].get(path,{}).get('sha256'))
                require(expected is not None and contract()['bindings'][path]==expected,'Parent verified asset binding')
                lineage+=1
        checks['completed_parent_lineage']=lineage==1560
        try:oldpackage(PREP/'packages'/contract()['roles'][0]['id']/'query.parquet',contract()['roles'][0],'H-predict')
        except RuntimeError:checks['premature_H_rejected']=True
        else:checks['premature_H_rejected']=False
        require(all(checks.values()),'Model/permission tests')
        write(OUT/'audits/unit-tests.json',dict(passed=True,checks=checks,new_fits=0,H_reads=0,U_reads=0))

if __name__=='__main__':run()
