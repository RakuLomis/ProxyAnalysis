"""Independent CUDA synthetic-input alias verification; no data packages or fit."""
import ast
import importlib.util
import os
from common import *


def run(contract):
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    import torch
    import torch.nn.functional as F
    require(torch.cuda.is_available(), 'CUDA required; no CPU replay fallback')
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    verifyseal(OUT/'manifests/models-complete.json')
    deploy_path = ROOT/'eval/post_input_associated_representation_v3/deploy.py'
    tree = ast.parse(deploy_path.read_text(encoding='utf-8'))
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    require(all((n.module if isinstance(n, ast.ImportFrom) else n.names[0].name).startswith('torch') for n in imports),
            'Standalone deployment imports a training/data module')
    spec = importlib.util.spec_from_file_location('unchanged_post_only_deploy', deploy_path)
    deploy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deploy)
    ACCESS.append(dict(path=rel(deploy_path), sha256=sha(deploy_path), purpose='unchanged-pure-inference-code'))
    generator = torch.Generator(device='cuda').manual_seed(20261014)
    raw = torch.rand((64, 96), generator=generator, device='cuda', dtype=torch.float64)
    offset = 0
    uniform = torch.zeros((1, 96), device='cuda', dtype=torch.float64)
    vertices = torch.zeros((10, 96), device='cuda', dtype=torch.float64)
    for width in [9]*4+[10]*6:
        raw[:, offset:offset+width] /= raw[:, offset:offset+width].sum(1, keepdim=True)
        uniform[:, offset:offset+width] = 1/width
        for i in range(10):
            vertices[i, offset+min(i, width-1)] = 1
        offset += width
    raw = torch.cat([raw, uniform, vertices])
    require(raw.shape == (75, 96), 'Synthetic input policy')
    endpoints = read(OUT/'manifests/endpoints.json')
    records = []
    with torch.no_grad():
        for r in contract['roles']:
            part = [e for e in endpoints if e['role_id'] == r['id']]
            require(len(part) == 12 and all(e['fallback'] and e['residual_path'] is None for e in part), 'Endpoint alias policy')
            path = ROOT/part[0]['base_path']; meta = read(path.with_suffix('.json'))
            original_path = ROOT/meta['source']
            model = torch.load(path, map_location='cuda', weights_only=True)
            original = torch.load(original_path, map_location='cuda', weights_only=True)
            ACCESS.extend([dict(path=rel(p), sha256=sha(p), purpose='frozen-base-parameters') for p in [path, original_path]])
            require(set(model) == set(original) == {'mu','scale','weight','bias'}, 'Model payload')
            require(all(torch.equal(model[k], original[k]) for k in model), 'Original model/scaler parameters differ')
            require(all(v.dtype == torch.float64 and bool(torch.isfinite(v).all()) for v in model.values()), 'Base dtype/finite')
            require(bool((model['scale'] > 0).all()), 'Scale positivity')
            x = (raw-original['mu'])/original['scale']
            z = x@original['weight'].T+original['bias']
            expected_lp = F.log_softmax(z, 1)
            expected_p = expected_lp.exp()
            expected_native_p = torch.softmax(z, 1)
            reference_logits = (raw-model['mu'])/model['scale']@model['weight'].T+model['bias']
            require(torch.equal(reference_logits, z), 'Fallback logit identity')
            for e in part:
                lp = deploy.predict_post(raw, model, residual_state=None)
                require(torch.equal(lp, expected_lp), 'Exact original-model logprob replay')
                require(torch.equal(lp.exp(), expected_p), 'Exact deployed probability alias')
                require(torch.equal(lp.argmax(1), z.argmax(1)), 'Exact class identity')
                require(torch.equal(torch.softmax(reference_logits, 1), expected_native_p), 'Original native-softmax identity')
            records.append(dict(role_id=r['id'], endpoints=12, cases=75,
                exact_original_parameters=True, logit_max_error=0., logprob_max_error=0.,
                probability_max_error=0., changed_classes=0,
                native_softmax_vs_logprob_exp_max_error=float((expected_native_p-expected_p).abs().max())))
    torch.cuda.synchronize()
    negative_checks = {}
    for name, invalid in [('cpu', raw.cpu()), ('float32', raw.float()), ('dimension', raw[:, :95])]:
        try:
            deploy.predict_post(invalid, model, None)
        except RuntimeError:
            negative_checks[name+'_rejected'] = True
        else:
            negative_checks[name+'_rejected'] = False
    require(all(negative_checks.values()), 'Post-only input guards')
    result = dict(passed=True, device=torch.cuda.get_device_name(0), torch_version=torch.__version__,
        replay_device='cuda:0', dtype='float64', original_deploy_unchanged=True,
        roles=60, endpoints=720, new_arm_fallback_seed_endpoints=540, reference_seed_endpoints=180,
        synthetic_rows_per_role=75, endpoint_case_replays=54000, unique_role_cases=4500,
        logit_max_error=0., logprob_max_error=0., probability_max_error=0., changed_classes=0,
        exact_original_parameters=True, all_checks=negative_checks,
        actual_H_post_reads=0, actual_H_pre_reads=0, actual_H_label_reads=0, actual_U_reads=0,
        new_training_fits=0, records=records,
        probability_convention='Exact alias under each same computation convention; native softmax and exp(log_softmax) may differ by floating-point rounding.',
        generality='Same frozen parameters/scaler and no residual establish function identity; synthetic cases validate wiring, not classification performance.')
    write(OUT/'audits/fallback-replay.json', result)
    print('CUDA_fallback_verified endpoints=720 cases=54000 max_error=0 changed_classes=0', flush=True)
    return result
