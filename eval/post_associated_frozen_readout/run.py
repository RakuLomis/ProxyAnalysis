"""Bounded v2 source readout experiment; never dispatch H or full-role training."""
from common import *
import register
import pipeline

def main():
    register.run()
    pipeline.pilot()
    pipeline.train()
    pipeline.predict()
    pipeline.score()
    pipeline.verify()
    pipeline.finish()

if __name__=='__main__':main()
