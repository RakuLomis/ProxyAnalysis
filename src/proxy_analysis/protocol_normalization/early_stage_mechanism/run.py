import argparse
from .common import freeze

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['tables','models','sample','sources','parse','report','all']);args=p.parse_args();freeze()
    if args.stage in ['tables','all']:
        from .statistics import build
        build()
    if args.stage in ['models','all']:
        from .statistics import models
        models()
    if args.stage in ['sample','all']:
        from .sampling import sample
        sample()
    if args.stage in ['sources','all']:
        from .sources import sources
        sources()
    if args.stage in ['parse','all']:
        from .logs import audit_logs
        audit_logs()
        from .capture import parse
        parse()
    if args.stage in ['report','all']:
        from .report import report
        report()

if __name__=='__main__':main()
