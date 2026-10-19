"""Separate inference/scoring processes enforce global model/prediction barriers."""
from common import *

def run(phase):
    configure('inference');begin(phase);hashes=code_seal(phase)
    try:
        from formal import source_model_seal,source_predict,selection,outer_model_seal,outer_predict
        from score import run as score
        from verify import run as verify
        from report import run as report
        fn={'source-seal':source_model_seal,'source-predict':source_predict,'selection':selection,
            'outer-seal':outer_model_seal,'outer-predict':outer_predict,'score':score,'verify':verify,'report':report}[phase]
        fn();codecheck(hashes)
    except BaseException as e:failure(phase,e);raise
    finally:end(phase)

if __name__=='__main__':run(sys.argv[1])
