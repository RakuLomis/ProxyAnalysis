"""Single registered numeric policy for every v4 main and pilot fit."""
SOLVER = 'cholesky-original-gradient-aware-lbfgs-v4'
POLICY = {
    'version': 'RA1-NR1-budget-only',
    'max_iter': 4000, 'max_eval': 20000,
    'original_gradient_max': 1e-5, 'objective_slack': 1e-10,
    'objective_replay_tolerance': 1e-10, 'gradient_replay_tolerance': 1e-10,
    'iteration_acceptance': 'strict_less_than_max_iter',
    'evaluation_limit_semantics': 'check_after_line_search',
    'initialization': 'zero', 'device': 'cuda:0', 'dtype': 'float64',
    'precision_gates_changed': False, 'iteration_budget_gate_changed': True,
    'all_arms_and_regularizers_share_policy': True,
}

def acceptance_gates(value, initial, gradient, iterations, error, gradient_error):
    return {
        'objective_nonincrease': bool(value <= initial+POLICY['objective_slack']),
        'original_coordinate_gradient': bool(gradient <= POLICY['original_gradient_max']),
        'iteration_budget': bool(iterations < POLICY['max_iter']),
        'objective_replay': bool(error < POLICY['objective_replay_tolerance']),
        'gradient_replay': bool(gradient_error < POLICY['gradient_replay_tolerance']),
    }
