"""NR2 algorithm; unchanged scientific objective and original end-point gates."""
SOLVER='cholesky-lbfgs1024-exact-newton32-NR2'
POLICY=dict(version='RA1-NR2-full',max_iter=4000,max_eval=20000,lbfgs_phase_updates=1024,newton_max_updates=32,
    original_gradient_max=1e-5,objective_slack=1e-10,objective_replay_tolerance=1e-10,gradient_replay_tolerance=1e-10,
    iteration_acceptance='strict_total_updates_less_than_max_iter',evaluation_limit_semantics='original_LBFGS_post_line_search_then_bounded_Newton',
    initialization='zero',device='cuda:0',dtype='float64',original_objective_unchanged=True,precision_gates_changed=False,
    solver_algorithm_changed=True,all_arms_and_regularizers_share_policy=True)
def acceptance_gates(value,initial,gradient,iterations,error,gradient_error):
    return dict(objective_nonincrease=bool(value<=initial+1e-10),original_coordinate_gradient=bool(gradient<=1e-5),
                iteration_budget=bool(iterations<4000),objective_replay=bool(error<1e-10),gradient_replay=bool(gradient_error<1e-10))
