"""Export observed pre/post scalar tables without using metadata as model input."""
from pathlib import Path
from ..paired_information.prepare import table
from ..paired_information.reference_retrain import SCALAR_NAMES
from ..reproducibility.preflight import write_table
from .business_features import load_config, verify


def main():
    cfg=load_config(); verify(cfg); root=Path(cfg['output_root'])
    records=[]
    for row in table(root/'side-summaries.parquet'):
        if row['selection']!='observed': continue
        record={k:row[k] for k in ('session_id','content_id','label_id','protocol','repetition','primary_candidate')}
        for side in ('pre','post'):
            record.update({side+'__'+name:row[side].get(name) for name in SCALAR_NAMES})
        records.append(record)
    dest=root/'paired-features.parquet'
    if dest.exists():
        if table(dest)!=records: raise ValueError('Existing paired export differs; refusing overwrite')
    else:
        write_table(dest,records)
    print({'paired_feature_rows':len(records),'primary_rows':sum(r['primary_candidate'] for r in records)})


if __name__=='__main__': main()
