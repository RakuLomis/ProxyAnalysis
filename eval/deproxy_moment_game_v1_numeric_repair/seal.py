"""Freeze executable sources before any numerical stage, append-only versions."""
from common import *
import difflib, ast

def freeze():
    version=1+len(list(OUT.glob('code-seal-*.json')))
    files={rel(p):sha(p) for p in sorted(CODE.glob('*.py'))}
    original=inspect.getsource(torch.optim.LBFGS.step)
    local=(CODE/'lbfgs_local.py').read_text(encoding='utf-8')
    local=local[local.index('    @torch.no_grad()'):]
    payload=dict(version=version,files=files,installed_lbfgs_sha256=sha(inspect.getfile(torch.optim.LBFGS)),
        diff=list(difflib.unified_diff(original.splitlines(),local.splitlines(),fromfile='installed.step',tofile='NER1.step')))
    require(payload['installed_lbfgs_sha256']==registration()['torch_lbfgs_sha256'],'Installed solver changed')
    p=OUT/f'code-seal-{version:02}.json';write(p,payload,True)
    # Current pointer copies a fully retained immutable stage version.
    write(OUT/'code-seal.json',payload)
    originals=ROOT/'eval/deproxy_moment_game_v1'
    bindings={}
    for name in ['simplex.py','moment_features.py','models.py','ridge_anchor.py']:
        a=(CODE/name).read_text(encoding='utf-8');b=(originals/name).read_text(encoding='utf-8')
        require(a.rstrip()==b.rstrip() and ast.dump(ast.parse(a))==ast.dump(ast.parse(b)),'Pure mathematics source differs '+name)
        bindings[name]=dict(copy_sha256=sha(CODE/name),original_sha256=sha(originals/name),
            AST_identical=True,text_identical_except_terminal_whitespace=True)
    write(OUT/f'pure-math-source-{version:02}.json',bindings,True)

if __name__=='__main__':freeze()
