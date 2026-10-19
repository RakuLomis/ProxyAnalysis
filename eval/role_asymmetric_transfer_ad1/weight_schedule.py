"""AD1 adds exactly two rho pairs, reusing the original label-indexed producer."""
from common import *
_path=PARENT_CODE/'weight_schedule.py'
_tree=ast.parse(_path.read_text(encoding='utf-8'))
_tree.body=[n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name in ['selection','slot']]
exec(compile(ast.fix_missing_locations(_tree),str(_path),'exec'),globals())
A='P__m025__UPR'
B='P__m025__SYM'
C_NEW='P__AD1_C000_U025'
D_NEW='P__AD1_C025_U050'
BASELINE='P__m010__SYM'
NAMES={A:'A: P-U50',B:'B: P-SYM25',C_NEW:'C: C0-U25',D_NEW:'D: C25-U50',BASELINE:'P-small'}
EFFECTS=[(D_NEW,A,'restore_C_at_U50'),(C_NEW,A,'reduce_U_at_C0'),
         (B,C_NEW,'restore_C_at_U25'),(D_NEW,B,'increase_U_at_C25')]

def registry():
    pairs=[(A,0.,.5),(B,.25,.25),(C_NEW,0.,.25),(D_NEW,.25,.5),(BASELINE,.1,.1)]
    return [dict(id=p,source='P',rho_C=rc,rho_U=ru,m=(rc+ru)/2,allocation='AD1-2x2',
                 existing=p in [A,B,BASELINE]) for p,rc,ru in pairs]
