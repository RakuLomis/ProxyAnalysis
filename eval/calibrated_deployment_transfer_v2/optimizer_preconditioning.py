"""Exact original objective in reversible curvature coordinates; original gates."""
import ast
import inspect
import textwrap
import types
from common import *

SOLVER = 'cholesky-initial-contrast-curvature-v1'
SETTINGS = dict(lr=1., max_iter=500, max_eval=625, history_size=100,
                tolerance_grad=1e-9, tolerance_change=1e-12, line_search_fn='strong_wolfe')

def coordinates(x, mass, t):
    a = torch.cat([x, torch.ones((len(x), 1), device=x.device, dtype=x.dtype)], 1)
    h = a.T@(a*mass[:, None])/6
    h = h+torch.diag(torch.cat([torch.full((96,), .001*(1+t), device=x.device, dtype=x.dtype),
                               torch.zeros(1, device=x.device, dtype=x.dtype)]))
    l = torch.linalg.cholesky(h)
    transformed = torch.linalg.solve_triangular(l, a.T, upper=False).T
    return a, l, transformed

def decode(v, l): return torch.linalg.solve_triangular(l.T, v.T, upper=True).T
def transformed_objective(v, l, a, y, mass, t):
    theta = decode(v, l)
    return (F.cross_entropy(a@v.T, y, reduction='none')*mass).sum()+.0005*(1+t)*theta[:, :96].square().sum()

def gates(value, initial, gradient, iterations, error, gradient_error):
    return {'objective_nonincrease': bool(value <= initial+1e-10),
            'original_coordinate_gradient': bool(gradient <= 1e-5),
            'iteration_budget': bool(iterations < 500),
            'objective_replay': bool(error < 1e-10), 'gradient_replay': bool(gradient_error < 1e-10)}

def observed_step(opt, record):
    # Insert observational calls before existing break/early-return statements.
    # The package/class is not patched, and optimizer arithmetic is unchanged.
    method = inspect.unwrap(torch.optim.LBFGS.step)
    source = textwrap.dedent(inspect.getsource(method)); tree = ast.parse(source)
    function = tree.body[0]; function.decorator_list = []
    class Observe(ast.NodeTransformer):
        def visit_If(self, node):
            self.generic_visit(node)
            if any(isinstance(s, (ast.Break, ast.Return)) for s in node.body):
                body = []
                for item in node.body:
                    if isinstance(item, (ast.Break, ast.Return)):
                        body.append(ast.Expr(ast.Call(ast.Name('_ct_record_stop', ast.Load()),
                            [ast.Constant(ast.unparse(node.test)), ast.Call(ast.Name('locals', ast.Load()), [], [])], [])))
                    body.append(item)
                node.body = body
            return node
    tree = Observe().visit(tree); ast.fix_missing_locations(tree)
    namespace = dict(method.__globals__)
    def hook(condition, local):
        record['condition'] = condition
        for key in ['n_iter', 'current_evals', 'max_iter', 'max_eval', 'loss', 'prev_loss', 'gtd', 't']:
            value = local.get(key)
            if value is not None: record[key] = float(value.detach()) if torch.is_tensor(value) else value
    namespace['_ct_record_stop'] = hook
    exec(compile(tree, '<observed-installed-lbfgs>', 'exec'), namespace)
    opt.step = types.MethodType(torch.no_grad()(namespace['step']), opt)

def fit_preconditioned(x, y, mass, t, context, diagnostic=False):
    basepath = OUT/('diagnostic-fit-logs' if diagnostic else 'fit-logs')/context['role_id']/f"{context['arm']}-t{t:g}.pt"
    failurepath = OUT/('diagnostic-failures' if diagnostic else 'failures')/context['role_id']/f"{context['arm']}-t{t:g}.pt"
    log = {**context, 'solver': SOLVER, 'settings': SETTINGS, 'initialization': 'zero',
           'device': 'cuda:0', 'dtype': 'float64', 'formal_fit': not diagnostic}
    v = l = opt = None; started = time.perf_counter(); stop = {}; calls = 0
    try:
        require(x.is_cuda and x.dtype == torch.float64, 'CUDA float64 required')
        require(x.shape[1] == 96 and abs(float(mass.sum())-1) < 1e-12, 'Fit coordinate/mass')
        require(torch.isfinite(x).all() and (mass > 0).all(), 'Invalid training values')
        require(float((weighted(y, mass, 6)-1/6).abs().max()) < 1e-12, 'Class mass changed')
        a, l, ax = coordinates(x, mass, t)
        v = torch.nn.Parameter(torch.zeros((6, 97), device=x.device, dtype=x.dtype))
        opt = torch.optim.LBFGS([v], **SETTINGS); observed_step(opt, stop)
        initial = float(transformed_objective(v, l, ax, y, mass, t).detach())
        def closure():
            nonlocal calls
            calls += 1; opt.zero_grad()
            value = transformed_objective(v, l, ax, y, mass, t)
            require(torch.isfinite(value), 'Nonfinite transformed objective'); value.backward(); return value
        opt.step(closure); value = float(closure().detach()); theta = decode(v.detach(), l)
        rw = theta[:, :96].clone().requires_grad_(); rb = theta[:, 96].clone().requires_grad_()
        logits = x@rw.T+rb
        replay = (mass*(torch.logsumexp(logits, 1)-logits.gather(1, y[:, None]).squeeze(1))).sum()
        replay = replay+.0005*(1+t)*rw.square().sum()
        gw, gb = torch.autograd.grad(replay, (rw, rb))
        original_gradient = torch.cat([gw, gb[:, None]], 1)
        chain_gradient = v.grad@l.T
        gradient = float(original_gradient.abs().max()); error = abs(float(replay.detach())-value)
        gradient_error = float((chain_gradient-original_gradient).abs().max())
        iterations = int(opt.state[v].get('n_iter', 0)); torch.cuda.synchronize()
        gate = gates(value, initial, gradient, iterations, error, gradient_error)
        log.update(initial_objective=initial, objective=float(replay.detach()), transformed_objective=value,
                   iterations=iterations, function_evaluations=int(opt.state[v].get('func_evals', 0)),
                   closure_evaluations=calls, max_gradient=gradient,
                   transformed_gradient_max=float(v.grad.abs().max()), objective_replay_error=error,
                   gradient_replay_error=gradient_error, gates=gate, accepted=all(gate.values()),
                   actual_optimizer_break=stop, seconds=time.perf_counter()-started,
                   budget_hit=iterations >= 500, cuda_peak_MiB=torch.cuda.max_memory_allocated()/1048576)
        write(basepath.with_suffix('.json'), log)
        require(all(gate.values()), 'Original-coordinate optimization quality gate; no budget extension')
        return {'weight': rw.detach(), 'bias': rb.detach()}, log
    except BaseException as exc:
        log.update(accepted=False, exception_type=type(exc).__name__, exception=str(exc),
                   seconds=time.perf_counter()-started, actual_optimizer_break=stop)
        write(failurepath.with_suffix('.json'), log)
        failurepath.parent.mkdir(parents=True, exist_ok=True)
        torch.save({'parameter_V': None if v is None else v.detach(), 'cholesky': l,
                    'optimizer_state': None if opt is None else opt.state_dict(),
                    'last_original_parameters': None if v is None or l is None else decode(v.detach(), l)},
                   writable(failurepath.with_suffix('.pt')))
        raise
