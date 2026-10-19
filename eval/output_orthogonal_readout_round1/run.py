import argparse
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','tests','pilot','train','predict','calibrate','score','audit','finish'])
    name=p.parse_args().stage
    if name=='register':
        import register;register.run()
    elif name=='tests':
        import tests;tests.run()
    elif name in ['pilot','train','predict']:
        import pipeline;{'pilot':pipeline.pilot,'train':pipeline.train_all,'predict':pipeline.predict}[name]()
    elif name=='calibrate':
        import calibration;calibration.run()
    elif name=='score':
        import score;score.run()
    else:
        import audit;{'audit':audit.run,'finish':audit.finish}[name]()

if __name__=='__main__':main()
