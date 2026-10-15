"""All-content prediction diagnostics; never select training data or weights."""
from common import *
from score import PC

DIAGNOSTIC_COMPARISONS=[('P-small','S'),('P-small','G-small'),*COMPARISONS]

def point(d):
    values=[]
    for (_,p,g),part in d.groupby(['arm','target','group']):
        m,_,_=metrics(truths(part),part[PC].to_numpy(),MASKS[g]);values.append(m['F1_uncovered'])
    return float(np.mean(values))

def run():
    with stage('concentration'):
        d=pd.read_parquet(OUT/'scores/labeled-predictions.parquet');rows=[]
        for (p,g,o),part in d.groupby(['target','group','outer']):
            for a,b in DIAGNOSTIC_COMPARISONS:
                x=part[part.arm.eq(a)].set_index('visit_id');y=part[part.arm.eq(b)].set_index('visit_id').loc[x.index]
                yy=truths(x);ac=x.prediction.to_numpy()==yy;bc=y.prediction.to_numpy()==yy
                xp=x[PC].to_numpy();yp=y[PC].to_numpy()
                for j,visit in enumerate(x.index):rows.append({'candidate':a,'reference':b,'target':p,'group':g,'outer':int(o),
                    'visit_id':visit,'content_id':x.iloc[j].content_id,'label_id':x.iloc[j].label_id,
                    'scope':'U' if yy[j] in MASKS[g] else 'C','fixed_error':bool(ac[j] and not bc[j]),
                    'new_error':bool(bc[j] and not ac[j]),'changed':bool(x.iloc[j].prediction!=y.iloc[j].prediction),
                    'probability_L1':float(np.abs(xp[j]-yp[j]).sum()),'delta_CE':float(-np.log(xp[j,yy[j]])+np.log(yp[j,yy[j]]))})
        df=pd.DataFrame(rows);require(len(df)==7200,'Five diagnostic comparisons x1440')
        save(df,OUT/'diagnostics/error-flips.parquet');summaries=[]
        for name,keys in [('overall',['candidate','reference']),('content',['candidate','reference','content_id','label_id']),
                     ('deployment',['candidate','reference','target']),('business-coverage',['candidate','reference','label_id','scope']),
                     ('content-role',['candidate','reference','target','group','content_id','label_id','scope'])]:
            agg=df.groupby(keys).agg(exposures=('visit_id','size'),unique_visits=('visit_id','nunique'),
                 repaired=('fixed_error','sum'),added=('new_error','sum'),changed=('changed','sum'),
                 mean_delta_CE=('delta_CE','mean'),mean_probability_L1=('probability_L1','mean')).reset_index()
            unique_fixed=df[df.fixed_error].groupby(keys).visit_id.nunique().rename('unique_fixed_visits')
            unique_added=df[df.new_error].groupby(keys).visit_id.nunique().rename('unique_added_visits')
            agg=agg.merge(unique_fixed,on=keys,how='left').merge(unique_added,on=keys,how='left').fillna({'unique_fixed_visits':0,'unique_added_visits':0})
            save(agg,OUT/'diagnostics'/(name+'.parquet'));summaries.append((name,agg))
        overall=dict(summaries)['overall'].set_index(['candidate','reference'])
        require(int(overall.loc[('P-small','S'),'repaired'])==33 and int(overall.loc[('P-small','S'),'added'])==16,'Old error-flip counts changed')
        content=dict(summaries)['content'];info=[]
        for (a,b),part in content.groupby(['candidate','reference']):
            info.append({'candidate':a,'reference':b,'contents':len(part),
              'contents_with_repairs':int((part.repaired>0).sum()),'contents_with_added_errors':int((part.added>0).sum()),
              'largest_content_repair_share':float(part.repaired.max()/max(1,part.repaired.sum())),
              'largest_content_added_share':float(part.added.max()/max(1,part.added.sum()))})
        write(OUT/'diagnostics/concentration.json',info)
        leave=[]
        for u in sorted(d.content_id.unique()):
            reduced=d[d.content_id.ne(u)];scores={a:point(reduced[reduced.arm.eq(a)]) for a in ARMS}
            for a,b in DIAGNOSTIC_COMPARISONS:leave.append({'excluded_content':u,'candidate':a,'reference':b,
                  'delta_uncovered_F1':scores[a]-scores[b],'retrained':False,'new_test':False})
        save(pd.DataFrame(leave),OUT/'diagnostics/leave-one-content.parquet')

if __name__=='__main__':run()
