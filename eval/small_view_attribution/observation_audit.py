"""Existing physical cache/window inventory, not an input reconstruction."""
from common import *
from compatibility import audit_read
import pyarrow.parquet as pq

SOURCES=[
 'docs/calibrated-deployment-business-transfer/v4/post-observation-boundary.md',
 'outputs/extend-calibration-20260930/run-01/extraction-03/prepared-windows.json',
 'outputs/extend-calibration-20260930/run-01/extraction-03/full-W-features.parquet',
 'outputs/extend-calibration-20260930/run-01/extraction-03/full-T-features.parquet',
 'outputs/extend-calibration-20260930/run-01/extraction-03/window-preflight.json']

def run():
    with stage('observation_audit'):
        for p in SOURCES:audit_read(p)
        windows=read(ROOT/SOURCES[1]);require(isinstance(windows,list),'Window list')
        rules=sorted({w['end_rule'] for w in windows});starts=sorted({w['start_rule'] for w in windows})
        schemas=[{'path':p,'rows':pq.read_metadata(ROOT/p).num_rows,'columns':pq.read_schema(ROOT/p).names} for p in SOURCES[2:4]]
        write(OUT/'audits/physical-post-qualification.json',{'inventory_complete':True,'physical_input_qualified':False,
            'existing_windows':len(windows),'start_rules':starts,'end_rules':rules,'schemas':schemas,
            'known_endpoint_filter_allowed_as_metadata':True,'independent_external_window_verified':False,
            'complete_physical_connection_reconstruction_verified':False,'PCAP_reads':0,'new_fits':0,
            'cache_only_inference_scope':'offline-associated visit input, model post-only',
            'future_requirements':['attacker-independent external window','all physical connections including unpaired/background',
                  'single-side direction and dedup state','fixed truncation/concurrency policy','separate finite-PCAP budget if needed']})

if __name__=='__main__':run()
