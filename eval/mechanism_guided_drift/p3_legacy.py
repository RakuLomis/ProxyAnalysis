"""Load frozen E1 functions without editing their files or confusing common modules."""
import importlib.util
import sys
from common import ROOT


def load():
    folder=ROOT/'eval/business_protocol_eval'
    names=['common','packages','generation','learning']
    saved={name:sys.modules.get(name) for name in names}
    modules={}
    try:
        for name in names:
            spec=importlib.util.spec_from_file_location('p3_frozen_'+name,folder/(name+'.py'))
            module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module;spec.loader.exec_module(module);modules[name]=module
    finally:
        for name,value in saved.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value
    return modules


LEGACY=load()
LC=LEGACY['common'];LP=LEGACY['packages'];LG=LEGACY['generation'];LE=LEGACY['learning']
