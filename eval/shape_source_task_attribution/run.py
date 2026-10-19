"""ST1 bounded source-inner experiment. Run with Pytorch312 and CUDA."""
import argparse
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['all','register','prepare','train','predict','score','verify','report'])
    args=p.parse_args()
    from prepare import register,prepare
    from train import train
    from evaluate import predict,score
    from verify import verify
    from report import report
    steps=dict(register=register,prepare=prepare,train=train,predict=predict,score=score,verify=verify,report=report)
    if args.stage=='all':
        for fn in steps.values():fn()
    else:steps[args.stage]()

if __name__=='__main__':main()
