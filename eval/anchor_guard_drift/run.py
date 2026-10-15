"""Single-use stage-one runner; intentionally has no classifier continuation."""
import importlib
from common import *

def run():
    require(not (OUT/'completion.json').exists(),'Completed run remains immutable')
    for name in ['inventory','prepare','tests','diagnostics','score','source_audit','report','verify']:
        importlib.import_module(name).run()

if __name__=='__main__':run()
