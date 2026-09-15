"""URL-clustered repeatability, exclusive separation and directional consistency."""
from __future__ import annotations

import argparse
from collections import defaultdict
import itertools
import math
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from scipy.stats import t
import yaml

from .preflight import write_json, write_table


def dispersion(values):
    x = np.asarray(values, dtype=float)
    median = float(np.median(x))
    mad = float(np.median(np.abs(x-median)))
    return {"n": len(x), "mean": float(x.mean()), "median": median,
            "variance": float(x.var(ddof=1)) if len(x)>1 else None,
            "sd": float(x.std(ddof=1)) if len(x)>1 else None,
            "mad_raw": mad, "mad_normal_scaled": mad / 0.6744897501960817,
            "iqr": float(np.quantile(x,.75)-np.quantile(x,.25)),
            "min": float(x.min()), "max": float(x.max())}


def icc(matrix):
    x = np.asarray(matrix, dtype=float)
    n,k = x.shape
    if n<2 or k<2:
        return None, None
    grand = x.mean()
    row = x.mean(axis=1,keepdims=True)
    col = x.mean(axis=0,keepdims=True)
    msr = k * np.square(row-grand).sum()/(n-1)
    msc = n * np.square(col-grand).sum()/(k-1)
    mse = np.square(x-row-col+grand).sum()/((n-1)*(k-1))
    single = msr+(k-1)*mse+k*(msc-mse)/n
    average = msr+(msc-mse)/n
    return (float((msr-mse)/single) if single>1e-15 else None,
            float((msr-mse)/average) if average>1e-15 else None)


def bounds(metric):
    if metric["transform"] == "log_ratio":
        return math.log(.9), math.log(1.1)
    return (-.05,.05) if metric["transform"] == "difference" else (0,.05)


def classify(values, metric):
    x=np.asarray(values,dtype=float)
    if len(x)<3:
        return {"classification":"uncertain", "ci95_low":None,"ci95_high":None,
                "ci90_low":None,"ci90_high":None}
    se=x.std(ddof=1)/math.sqrt(len(x))
    a,b=t.ppf(.975,len(x)-1)*se,t.ppf(.95,len(x)-1)*se
    low,high=bounds(metric)
    mean=float(x.mean())
    label="uncertain"
    if metric["transform"] == "distance":
        if mean-a>high:
            label="distance_above_threshold"
        elif mean+b<high:
            label="distance_within_threshold"
    elif mean-a>high:
        label="increase"
    elif mean+a<low:
        label="decrease"
    elif mean-b>low and mean+b<high:
        label="practically_stable"
    return {"classification":label,"ci95_low":mean-a,"ci95_high":mean+a,
            "ci90_low":mean-b,"ci90_high":mean+b}


def bh(values):
    a=np.asarray(values,dtype=float)
    order=np.argsort(a)
    q=np.minimum.accumulate((a[order]*len(a)/np.arange(1,len(a)+1))[::-1])[::-1]
    out=np.empty_like(a)
    out[order]=np.clip(q,0,1)
    return out.tolist()


def separability(cube, epsilon):
    # Dimensions: URL, protocol, repetition; never pool URL variance into W.
    x=np.asarray(cube,dtype=float)
    means=x.mean(axis=2)
    within=x.var(axis=2,ddof=1).mean(axis=1)
    between=means.var(axis=1,ddof=1)
    return between,within,float(between.mean()/(within.mean()+epsilon)),float(
        means.mean(axis=0).var(ddof=1)/(within.mean()+epsilon))


def signflip_p(differences):
    x=np.asarray(differences,dtype=float)
    observed=abs(x.mean())
    if len(x)>18:
        raise ValueError("exact sign flip limited to18 URL clusters")
    count=0
    total=2**len(x)
    for signs in itertools.product((-1,1),repeat=len(x)):
        count+=abs(np.dot(x,signs)/len(x))>=observed-1e-14
    return count/total


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root",type=Path)
    parser.add_argument('--config', type=Path, default=Path('configs/reproducibility.yaml'))
    args=parser.parse_args()
    root=args.output_root
    config=yaml.safe_load(args.config.read_text(encoding='utf-8'))
    metrics={m["id"]:m for m in config["metrics"]}
    rng=np.random.default_rng(config["seed"])
    bootstrap=config["bootstrap_repetitions"]
    rows=pq.read_table(root/"repeat_feature_long.parquet").to_pylist()
    keys=[(r['session_id'],r['scope'],r['selection'],r['metric']) for r in rows]
    if len(keys)!=len(set(keys)):
        raise ValueError('duplicate repeated feature identity')
    domain_targets = defaultdict(set)
    for row in rows:
        domain_targets[row['target_domain']].add(row['activity_id'])
    if any(len(v) != 1 for v in domain_targets.values()):
        raise ValueError('repeat statistics requires one fixed activity per domain; refusing to collapse targets')
    if {r['repetition'] for r in rows if r['is_final']} != set(range(1, 6)):
        raise ValueError('five-round registered repeat design required; broad data is not applicable')
    eligibility={r["session_id"]:r for r in pq.read_table(root/"routing_eligibility.parquet").to_pylist()}
    valid=[r for r in rows if r["is_final"] and r["delta"] is not None
           and eligibility[r["session_id"]]["page_context_candidate"]]
    a_rows,icc_rows,b_rows,c_rows,local_direction,sensitivity=[],[],[],[],[],[]
    low_variability={"example.com","wikipedia.org","developer.mozilla.org","github.com","arxiv.org"}
    for stratum, reps in (("all5",list(range(1,6))),("rounds2to5",list(range(2,6)))):
        route_rows=list(eligibility.values())
        balanced={u for u in {r['target_domain'] for r in route_rows}
                  if all({r['repetition'] for r in route_rows if r['target_domain']==u
                          and r['protocol']==p and r['page_context_candidate']} >= set(reps)
                         for p in ('SHADOWSOCKS','VLESS','HYSTERIA2'))}
        for selection in ("observed","nonempty","exclude_full_retransmission"):
            for cohort in ("page_proxy", "main_document_proxy", "low_variability", "no_retry", "balanced_three"):
                subset=[r for r in valid if r["repetition"] in reps and r["selection"]==selection
                        and (cohort!="main_document_proxy" or eligibility[r["session_id"]]["main_document_proxy_candidate"])
                        and (cohort!="low_variability" or r["target_domain"] in low_variability)
                        and (cohort!="balanced_three" or r["target_domain"] in balanced)
                        and (cohort!="no_retry" or r["is_first_attempt"])]
                grouped=defaultdict(dict)
                for r in subset:
                    key=(r["scope"],r["protocol"],r["metric"],r["target_domain"])
                    if r["repetition"] in grouped[key]:
                        raise ValueError(f"duplicate repeated feature: {key}")
                    grouped[key][r["repetition"]]=r["delta"]
                base={"stratum":stratum,"selection":selection,"cohort":cohort}
                icc_groups=defaultdict(list)
                for (scope,protocol,metric,domain),values in grouped.items():
                    x=[values[r] for r in sorted(values)]
                    d=dispersion(x)
                    low,high=bounds(metrics[metric])
                    a_rows.append({**base,"scope":scope,"protocol":protocol,"metric":metric,
                                   "target_domain":domain,**d,"values":x,
                                   "repetitions":sorted(values),"complete":set(values)==set(reps),
                                   "mad_over_threshold":d["mad_raw"]/high,
                                   "rank_eligible":len(x)>=3})
                    local_direction.append({**base,"scope":scope,"protocol":protocol,"metric":metric,
                                            "target_domain":domain,**classify(x,metrics[metric]),
                                            "n":len(x),"mean":d["mean"]})
                    if set(values)==set(reps):
                        icc_groups[(scope,protocol,metric)].append([values[r] for r in reps])
                # Bootstrap ICC only primary selection/cohort; other strata retain point estimates.
                for (scope,protocol,metric),matrix in icc_groups.items():
                    single,average=icc(matrix)
                    lo=hi=None
                    finite=[]
                    if len(matrix)>=3 and selection=="observed" and cohort=="page_proxy":
                        x=np.asarray(matrix)
                        for indices in rng.integers(0,len(x),size=(bootstrap,len(x))):
                            score=icc(x[indices])[0]
                            if score is not None: finite.append(score)
                        if finite: lo,hi=map(float,np.quantile(finite,[.025,.975]))
                    icc_rows.append({**base,"scope":scope,"protocol":protocol,"metric":metric,
                                     "n_urls":len(matrix),"k_repetitions":len(reps),
                                     "icc_A1":single,"icc_Ak":average,"ci95_low":lo,"ci95_high":hi,
                                     "bootstrap_finite":len(finite),
                                     "interpretation":"absolute_agreement_random_rounds_model"})
                family=[]
                for metric in metrics:
                    domains=sorted({key[3] for key in grouped if key[0]=="exclusive_page" and key[2]==metric})
                    common=[u for u in domains if all(set(grouped.get(("exclusive_page",p,metric,u),{}))==set(reps)
                            for p in ("SHADOWSOCKS","VLESS"))]
                    if len(common)<3: continue
                    cube=np.asarray([[[grouped[("exclusive_page",p,metric,u)][r] for r in reps]
                                      for p in ("SHADOWSOCKS","VLESS")] for u in common])
                    epsilon=1e-6*bounds(metrics[metric])[1]**2
                    between,within,local_s,global_s=separability(cube,epsilon)
                    diffs=cube[:,1,:].mean(axis=1)-cube[:,0,:].mean(axis=1)
                    boot_indices=rng.integers(0,len(common),size=(bootstrap,len(common)))
                    means=diffs[boot_indices].mean(axis=1)
                    ci=np.quantile(means,[.025,.975])
                    s_boot=between[boot_indices].mean(axis=1)/(within[boot_indices].mean(axis=1)+epsilon)
                    s_ci=np.quantile(s_boot,[.025,.975])
                    out={**base,"scope":"exclusive_page","metric":metric,"row_type":"summary",
                         "n_urls":len(common),"repetitions":len(reps),
                         "between_variance":float(between.mean()),"within_variance":float(within.mean()),
                         "S_local_pooled":local_s,"S_global":global_s,"S_ci95_low":float(s_ci[0]),
                         "S_ci95_high":float(s_ci[1]),"epsilon":epsilon,
                         "difference_VLESS_minus_SS":float(diffs.mean()),"ci95_low":float(ci[0]),
                         "ci95_high":float(ci[1]),"p_value":signflip_p(diffs),
                         "test":"URL_cluster_sign_symmetry_not_schedule_randomization",
                         "near_zero_W":bool(within.mean()<100*epsilon)}
                    family.append(out)
                    for factor in (.1,1,10):
                        sensitivity.append({**base,"metric":metric,"check":"epsilon_factor",
                                            "factor":factor,"S_min":separability(cube,epsilon*factor)[2]})
                    for i,u in enumerate(common):
                        b_rows.append({**base,"scope":"exclusive_page","metric":metric,"row_type":"url",
                                       "target_domain":u,"between_variance":float(between[i]),
                                       "within_variance":float(within[i]),
                                       "S_local_pooled":float(between[i]/(within[i]+epsilon)),
                                       "difference_VLESS_minus_SS":float(diffs[i])})
                    # Explicit block/URL deletion checks, preserving paired protocols.
                    for axis,label in ((0,"leave_one_url_out"),(2,"leave_one_round_out")):
                        scores=[]
                        differences=[]
                        for i in range(cube.shape[axis]):
                            sample=np.delete(cube,i,axis=axis)
                            scores.append(separability(sample,epsilon)[2])
                            differences.append(float((sample[:,1,:]-sample[:,0,:]).mean()))
                        sensitivity.append({**base,"metric":metric,"check":label,
                                            "S_min":min(scores),"S_max":max(scores),
                                            "difference_min":min(differences),"difference_max":max(differences)})
                for item,q in zip(family,bh([r["p_value"] for r in family])):
                    b_rows.append({**item,"q_value":q})
    aggregate=defaultdict(list)
    for r in local_direction:
        aggregate[tuple(r[k] for k in ("stratum","selection","cohort","scope","protocol","metric"))].append(r)
    for key,group in aggregate.items():
        counts={label:sum(r["classification"]==label for r in group) for label in
                ("increase","decrease","practically_stable","uncertain",
                 "distance_above_threshold","distance_within_threshold")}
        eligible=[r for r in group if r["n"]>=3]
        c_rows.append({**dict(zip(("stratum","selection","cohort","scope","protocol","metric"),key)),
                       "n_urls_observed":len(group),"n_urls_n_ge_3":len(eligible),**counts,
                       "increase_fraction":counts["increase"]/len(eligible) if eligible else None,
                       "decrease_fraction":counts["decrease"]/len(eligible) if eligible else None,
                       "stable_fraction":counts["practically_stable"]/len(eligible) if eligible else None})
    # Explicit schemas inferred over all keys, not only sparse first row.
    def uniform(records):
        keys=set().union(*(r.keys() for r in records))
        return [{k:r.get(k) for k in sorted(keys)} for r in records]
    for name,records in (("within_protocol_repeatability",a_rows),("repeatability_icc",icc_rows),
                         ("between_protocol_separation",b_rows),("cross_url_consistency",c_rows),
                         ("url_direction_classification",local_direction),("reproducibility_sensitivity",sensitivity)):
        write_table(root/(name+".parquet"),uniform(records))
    write_json(root/"statistics-summary.json",{"within_rows":len(a_rows),"icc_rows":len(icc_rows),
        "separation_rows":len(b_rows),"consistency_rows":len(c_rows),"seed":config["seed"],
        "bootstrap_repetitions":bootstrap,"hy2_separation_inference":False,
        "inference_limitations":["URL clusters may share round-level network conditions",
        "ICC random-round model is an assumption; only4/5 rounds observed",
        "Per-URL t intervals assume independent repeat errors; classifications are descriptive",
        "Exploratory small-sample results; no pure protocol causal attribution"]})
    print(f"Wrote A={len(a_rows)}, B={len(b_rows)}, C={len(c_rows)} rows")


if __name__ == "__main__":
    main()
