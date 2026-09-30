"""Independent arithmetic audit of the fixed P4 tables."""
from collections import defaultdict
import math

import numpy as np
from scipy.spatial.distance import jensenshannon

from .mechanism_contract import verify, read
from ..paired_information.prepare import table, digest
from ..reproducibility.preflight import write_json


def main():
    cfg,business,source,root=verify(); out=root/'p4-transformation'
    for path,expected in read(out/'contract.json')['sources'].items():
        if digest(path)!=expected: raise ValueError('P4 source changed')
    for name,expected in read(out/'complete.json')['artifacts'].items():
        if digest(out/name)!=expected: raise ValueError('P4 output changed')
    sources={}
    for batch,path in [('0914','outputs/paired-information-0914/run-01/side-summaries.parquet'),
                       ('0916',source/'side-summaries.parquet')]:
        for r in table(path):
            if r['selection']=='observed': sources[(batch,r['session_id'])]=r
    records=table(out/'session-transformations.parquet'); groups=defaultdict(list)
    for r in records:
        original=sources[(r['cohort'][:4],r['session_id'])]
        if r['metric'] in ('length_js','iat_js'):
            key='length_hist' if r['metric']=='length_js' else 'iat_hist'
            a=np.asarray(original['pre'][key],float); b=np.asarray(original['post'][key],float)
            expected=float(jensenshannon(a/a.sum(),b/b.sum(),base=2)**2) if a.sum() and b.sum() else None
        else:
            a,b=original['pre'][r['metric']],original['post'][r['metric']]
            expected=math.log(b)-math.log(a) if a is not None and b is not None and a>0 and b>0 else None
        if (expected is None)!=(r['delta'] is None) or (expected is not None and not np.isclose(expected,r['delta'],atol=1e-12,rtol=1e-10)):
            raise ValueError('P4 transformation arithmetic mismatch')
        groups[(r['cohort'],r['protocol'],r['resource_identity'],r['metric'])].append(expected)
    contents=table(out/'content-repeatability.parquet')
    if len(contents)!=len(groups): raise ValueError('Content coverage mismatch')
    for r in contents:
        values=groups[(r['cohort'],r['protocol'],r['resource_identity'],r['metric'])]
        x=np.asarray([v for v in values if v is not None]); median=float(np.median(x))
        expected=[median,float(np.median(np.abs(x-median))),float(np.percentile(x,75)-np.percentile(x,25))]
        if not np.allclose(expected,[r['median_delta'],r['mad_delta'],r['iqr_delta']],atol=1e-12,rtol=1e-10):
            raise ValueError('Content median/MAD/IQR mismatch')
    for r in read(out/'group-summary.json'):
        group=[v for v in contents if v['cohort']==r['cohort'] and v['protocol']==r['protocol'] and v['metric']==r['metric']
               and (r['level']=='all' or (r['level']=='overlap' and v['overlap']==r['group'])
                    or (r['level']=='business' and v['label_id']==r['group']))]
        if len(group)!=r['contents'] or not np.isclose(np.median([v['median_delta'] for v in group]),r['median_content_delta']):
            raise ValueError('Equal-content aggregation mismatch')
    dest=out/'independent-validation.json'
    if dest.exists(): raise ValueError('Audit output exists')
    result={'passed':True,'checked_session_metrics':len(records),'checked_content_metrics':len(contents),
            'independent_JS':'scipy Jensen-Shannon distance squared, base2',
            'no_models_or_raw_packet_parsing':True,'audit_code_sha256':digest(__file__)}
    write_json(dest,result); print(result)


if __name__=='__main__': main()
