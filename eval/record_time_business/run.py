import argparse
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'src'))
from proxy_analysis.crosscontent.record_time_business.data import freeze,extract,coverage
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['freeze','extract','coverage','data','tensors','prepare','engineering','audit','cuda-benchmark','formal'],default='data');a=p.parse_args()
if a.stage in ['freeze','data']:freeze()
if a.stage in ['extract','data']:extract()
if a.stage in ['coverage','data']:coverage()
if a.stage=='tensors':
    from proxy_analysis.crosscontent.record_time_business.tensors import build
    build()
if a.stage=='prepare':
    from proxy_analysis.crosscontent.record_time_business.tensors import prepare
    prepare()
if a.stage=='engineering':
    from proxy_analysis.crosscontent.record_time_business.engineering import engineer
    engineer()
if a.stage=='audit':
    from proxy_analysis.crosscontent.record_time_business.delivery import finish_engineering
    finish_engineering()
if a.stage=='cuda-benchmark':
    from proxy_analysis.crosscontent.record_time_business.cuda_benchmark import benchmark
    benchmark()
if a.stage=='formal':
    from proxy_analysis.crosscontent.record_time_business.formal import run
    run()
