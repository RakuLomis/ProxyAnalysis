"""JAT1 staged implementation; full scientific execution is not auto-started."""
import argparse
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','tests','profile','pilot','all']);p.add_argument('--tag')
    p.add_argument('--qualification-tag')
    args=p.parse_args()
    if args.stage=='register':
        from register import register
        register()
    elif args.stage=='tests':
        require(args.tag,'Explicit engineering version tag required')
        from tests import tests
        tests(args.tag)
    elif args.stage=='profile':
        require(args.tag,'Explicit profiling version tag required')
        from gpu_profile import profile
        profile(args.tag,args.qualification_tag)
    else:
        from workflow import run
        run(args.stage)

if __name__=='__main__':main()
