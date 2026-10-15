"""Execute unchanged frozen model-selection, inference, score and plot procedures."""
from common import *

def run(action):
    if action in ['inner-fit','inner-predict','select','outer-fit','predict']:
        m=load_frozen('main_experiment')
        {'inner-fit':lambda:m.fit_roles(True),'inner-predict':m.inner_predict,'select':m.select,
         'outer-fit':lambda:m.fit_roles(False),'predict':m.outer_predict}[action]()
    elif action in ['score','explain']:
        m=load_frozen('score');{'score':m.run,'explain':m.explain}[action]()
    elif action=='observation':load_frozen('report').observation_inventory()
    elif action=='plots':load_frozen('plots').run()
    else:raise ValueError(action)

if __name__=='__main__':
    import sys
    run(sys.argv[1])
