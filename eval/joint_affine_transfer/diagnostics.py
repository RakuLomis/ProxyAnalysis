"""Offline forward recovery after ALL classifications are sealed."""
from common import *
import affine

def run():
    c=start('diagnostics');sealed_predictions();selected=choices();rows=[];coeff=[];shapes=[]
    for index,r in enumerate(c['roles']):
        d=package(ROOT/r['heldout_visits'],'explain-visits')
        require(set(d.protocol)=={r['calibration']} and set(d.content_id)==set(r['validation_contents']),'Recovery scope')
        for arm in ARMS:
            v=chosen(r,arm,selected);eta=v['eta'];m=get(mappath(r,arm,eta))
            x=(tensor(d[['pre_'+h for h in HIST]])-m['mu'])/m['scale']
            y=(tensor(d[['post_'+h for h in HIST]])-m['mu'])/m['scale']
            predicted=affine.apply(m,x);error=predicted-y
            for j,a in enumerate(d.to_dict('records')):
                row={k:a[k] for k in ['visit_id','content_id','label_id']}
                row.update(role_id=r['id'],target=r['target'],calibration=r['calibration'],outer=r['outer'],
                           inner=r['inner'],group=r['group'],arm=arm,eta=eta,MSE=float(error[j].square().mean()),
                           coordinate_bias=float(error[j].mean()),test_pre_used_for_classification=False)
                for k in range(10):row['MSE_'+FEATURES[k]]=float(error[j,block(k)].square().mean())
                rows.append(row)
            if r['inner'] is None:
                for j in range(10):
                    for k in range(10):coeff.append({'role_id':r['id'],'arm':arm,'output_block':FEATURES[j],
                        'input_block':FEATURES[k],'Frobenius_norm':float(m['matrix'][block(j),block(k)].norm()),
                        'causal_attribution':False})
                shapes.append({'role_id':r['id'],'arm':arm,**read(slotpath(r,arm,eta).with_suffix('.json'))['shape']})
        if index%50==0:progress('JA_offline_recovery',roles=index,total=780)
    save(pd.DataFrame(rows),OUT/'diagnostics/recovery.parquet')
    save(pd.DataFrame(coeff),OUT/'diagnostics/cross-block-coefficients.parquet')
    save(pd.DataFrame(shapes),OUT/'diagnostics/source-view-shape.parquet')
    write(OUT/'diagnostics/complete.json',{'rows':len(rows),'prediction_seal_sha256':sha(OUT/'predictions/complete.json'),
        'model_fits':0,'selection_outputs_written':False,'test_pre_input_to_classifier':False})
    finish('diagnostics',rows=len(rows),new_fits=0)

if __name__=='__main__':run()
