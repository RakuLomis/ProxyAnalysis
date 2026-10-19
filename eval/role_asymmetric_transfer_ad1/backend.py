"""Original NR2 forward solver and original-coordinate acceptance, new IO only."""
from common import *
exec(compile((PARENT_CODE/'backend.py').read_text(encoding='utf-8'),str(PARENT_CODE/'backend.py'),'exec'),globals())
