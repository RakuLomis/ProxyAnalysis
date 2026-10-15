"""Finite pilot, then promotion gate. No H scoring during pilot."""
from common import *
from selection import baseline,fit_role,weights
from mappings import mapped_views
from objectives import fit
from representation import predict

def slots(r):
    result={}
    for rep in ['M','I','J']:
        b=baseline(r,rep); result[rep+'-S']={k:b[k] for k in ['x','y','mass','mu','scale']}
        if rep!='J':continue
        rootdir=rolepath(r)/'J'; pre=package(rootdir/'source-pre.parquet','train')
        px=(tensor(pre[INPUTS['J']])-b['mu'])/b['scale']; n=len(b['source'])
        py=tensor(truths(pre),torch.long); pm,_=weights().loss_weights(pre,b['cp'],r['missing'])
        require(torch.equal(py,artifact(ROOT/r['reuse_views'])['P_y']),'Independent pre own labels replay')
        mapped=mapped_views(r,b['mu'],b['scale'],px)
        views={'P':(mapped['P'],py,pm[n:2*n]),'G':(mapped['G'],py,pm[n:2*n]),
               'RawPre':(px,py,pm[n:2*n]),'RawPost':(b['main_x'],b['y'][:n],b['mass'][:n]),
               'Marginal':(mapped['Marginal'],py,pm[n:2*n])}
        for key,(x,y,m) in views.items():
            result['J-'+key+'-small']={'x':torch.cat([b['main_x'],b['S_x'],x,b['C_x']]),
                'y':torch.cat([b['y'][:n],b['y'][n:2*n],y,b['y'][2*n:]]),
                'mass':torch.cat([b['mass'][:n],.9*b['mass'][n:2*n],.1*m,b['mass'][2*n:]]),
                'mu':b['mu'],'scale':b['scale']}
    return result

def run(pilot):
    name='numeric_pilot' if pilot else 'formal_remaining'
    with stage(name):
        require((OUT/'stages/diagnostic_score.json').exists(),'C diagnostic stage incomplete')
        extension=OUT/'manifests/learning-code.json'
        require(sha(extension)==read(extension.with_name('learning-code-seal.json'))['sha256'],'Learning code seal')
        for p,h in read(extension)['sha256'].items():checked(ROOT/p,h,'learning-code')
        c=contract(); roles=[r for r in c['roles'] if (r['outer']==0)==pilot]
        if not pilot:require(read(OUT/'pilot/promotion.json')['passed'],'Numeric pilot promotion needed')
        started=time.perf_counter(); results=[]; fit_count=0
        for index,r in enumerate(roles):
            choices=fit_role(r); fit_count+=24
            choices={v['representation']:v['t'] for v in choices}; bag=slots(r)
            for arm in ARMS:
                rep=arm[0]; t=choices[rep]; s=bag[arm]; p=OUT/'models/outer'/r['id']/(arm+'.pt')
                if p.with_suffix('.json').exists():model=artifact(p); log=read(p.with_suffix('.json'))['optimizer']
                else:
                    m,log=fit(s['x'],s['y'],s['mass'],t,{'role_id':r['id'],'arm':arm})
                    model={**m,'mu':s['mu'],'scale':s['scale']}; put(model,p,optimizer=log,role_id=r['id'],arm=arm,t=t)
                q=package(rolepath(r)/rep/'query.parquet','query'); d=predict(model,q,rep)
                d['role_id']=r['id']; d['arm']=arm
                save(d,OUT/'predictions/by-role'/r['id']/(arm+'.parquet'))
                results.append({'role_id':r['id'],'arm':arm,'t':t,'seconds':log['seconds'],'max_gradient':log['max_gradient']})
                fit_count+=1
            progress(name+'_roles',roles=index+1,total=len(roles),classification_endpoints=fit_count)
        require(fit_count==(384 if pilot else 1536),'Finite classifier budget')
        save(pd.DataFrame(results),OUT/('pilot' if pilot else 'formal')/'outer-endpoints.parquet')
        if pilot:
            seconds=time.perf_counter()-started
            write(OUT/'pilot/promotion.json',{'passed':True,'classifiers':384,'inner':288,'outer':96,'H_labels_read':False,
                'seconds':seconds,'remaining_classifier_endpoints':1536,'rough_remaining_seconds':4*seconds,
                'estimate_not_completion_promise':True,'automatic_full_launch':False})
        else:
            preds=[]
            for r in c['roles']:
                for arm in ARMS:preds.append(pd.read_parquet(OUT/'predictions/by-role'/r['id']/(arm+'.parquet')))
            d=pd.concat(preds,ignore_index=True); require(len(d)==11520,'Prediction budget')
            p=OUT/'predictions/visits.parquet'; save(d,p)
            write(p.with_name('complete.json'),{'sha256':sha(p),'rows':len(d),'H_labels_read':False})

if __name__=='__main__':run(sys.argv[1]=='pilot')
