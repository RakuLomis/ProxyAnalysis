"""Read-only fixture use; deliberate corruptions are confined to pytest temp dirs."""
import shutil
from pathlib import Path

import pytest

from proxy_analysis.crosscontent.mechanism_contract import settings, cohort, read
from proxy_analysis.crosscontent.mechanism_report import audit_job
from proxy_analysis.paired_information.prepare import digest, table
from proxy_analysis.reproducibility.preflight import write_json, write_table


def audited_copy(tmp_path):
    cfg,business,source,out=settings()
    job=out/'jobs/youtube_activity-SHADOWSOCKS-0-scalar14'
    if not (job/'complete.json').exists(): pytest.skip('Local frozen integration fixture unavailable')
    dest=tmp_path/'job'; shutil.copytree(job,dest)
    lookup={r['session_id']:r for r in cohort(source)}
    assignment=read(source/'learning/outer-splits.json')
    return dest,lookup,assignment,cfg


def rehash(dest,name):
    complete=read(dest/'complete.json'); complete['artifacts'][name]=digest(dest/name)
    write_json(dest/'complete.json',complete)


def test_independent_audit_rejects_non_source_preprocessing(tmp_path):
    dest,lookup,assignment,cfg=audited_copy(tmp_path)
    audit_job(dest,lookup,assignment,cfg)
    ledger=read(dest/'fit-ledger.json'); ledger[0]['state']['scaler_mean'][0]+=1
    write_json(dest/'fit-ledger.json',ledger); rehash(dest,'fit-ledger.json')
    with pytest.raises(ValueError,match='preprocessing'):
        audit_job(dest,lookup,assignment,cfg)


def test_independent_audit_rejects_wrong_joint_identity(tmp_path):
    dest,lookup,assignment,cfg=audited_copy(tmp_path)
    maps=table(dest/'pair-maps.parquet')
    for m in maps:
        if m['arm']=='J-Wrong':
            m['donor']=m['receiver']; break
    write_table(dest/'pair-maps.parquet',maps); rehash(dest,'pair-maps.parquet')
    with pytest.raises(ValueError,match='cross-content'):
        audit_job(dest,lookup,assignment,cfg)
