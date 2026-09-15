"""Exploratory paired workload adjustment, without causal claims or new dependencies."""
import argparse
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from .preflight import write_table


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('output_root',type=Path)
    root=parser.parse_args().output_root
    eligibility={r['session_id']:r['page_context_candidate'] for r in pq.read_table(root/'routing_eligibility.parquet').to_pylist()}
    rows=[r for r in pq.read_table(root/'repeat_feature_long.parquet').to_pylist()
          if r['is_final'] and r['scope']=='exclusive_page' and r['selection']=='observed'
          and eligibility[r['session_id']] and r['delta'] is not None]
    for domain in {r['target_domain'] for r in rows}:
        if len({r['activity_id'] for r in rows if r['target_domain']==domain}) != 1:
            raise ValueError('workload sensitivity requires one activity per domain')
    if {r['repetition'] for r in rows} != set(range(1,6)):
        raise ValueError('five-round workload sensitivity only')
    index={(r['target_domain'],r['repetition'],r['protocol'],r['metric']):r for r in rows}
    results=[]
    for stratum,reps in [('all5',range(1,6)),('rounds2to5',range(2,6))]:
        for metric in sorted({r['metric'] for r in rows}):
            domains=sorted({r['target_domain'] for r in rows})
            complete=[u for u in domains if all((u,r,p,m) in index for r in reps
                for p in ('SHADOWSOCKS','VLESS') for m in (metric,'transport_bytes','entity_count'))]
            if len(complete)<3:continue
            design=[];target=[]
            for u in complete:
                for r in reps:
                    ss=lambda m:index[(u,r,'SHADOWSOCKS',m)]
                    vl=lambda m:index[(u,r,'VLESS',m)]
                    workload=np.log(vl('transport_bytes')['pre']/ss('transport_bytes')['pre'])
                    entities=np.log(vl('entity_count')['pre']/ss('entity_count')['pre'])
                    design.append([1,workload,entities,*[float(r==v)-1/len(reps) for v in list(reps)[1:]],
                                   *[float(u==v)-1/len(complete) for v in complete[1:]]])
                    target.append(vl(metric)['delta']-ss(metric)['delta'])
            x=np.asarray(design);y=np.asarray(target)
            # Remove zero covariates only. Other rank deficiencies are reported, not hidden.
            keep=np.any(np.abs(x)>1e-12,axis=0)
            x=x[:,keep]
            beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
            results.append({'stratum':stratum,'metric':metric,'n_urls':len(complete),'n_paired_visits':len(y),
                            'unadjusted_difference':float(y.mean()),
                            'adjusted_difference_at_equal_pre_workload_entities':float(beta[0]) if rank==x.shape[1] else None,
                            'rank':int(rank),'columns':x.shape[1],'condition_number':float(np.linalg.cond(x)),
                            'residual_sd':float(np.std(y-x@beta,ddof=1)),
                            'interpretation':'exploratory_paired_OLS_URL_round_FE_no_pvalue_no_causality'})
    write_table(root/'pre_workload_adjustment.parquet',results)
    print(f'Wrote {len(results)} workload-adjustment rows')


if __name__=='__main__':main()
