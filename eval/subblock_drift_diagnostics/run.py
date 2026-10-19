"""Run or resume only the frozen SD1 stages, no training entry point."""
import argparse
from .common import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['all', 'P0', 'P1', 'P2', 'P3', 'P4', 'P5'], default='all')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--verify-only', action='store_true', help='Check terminal files and seals without fitting or scoring')
    args = parser.parse_args()
    configure()
    if args.verify_only:
        c = contract()
        for p, info in c['files'].items():
            need(sha(ROOT/p) == info['sha256'], 'Changed input '+p)
        for p, h in c['source_sha256'].items():
            need(sha(ROOT/p) == h, 'Changed SD1 code '+p)
        need(sha(PLAN) == c['plan_sha256'], 'Plan changed')
        for p, h in read(OUT/'ledger.json')['output_files'].items():
            need(sha(ROOT/p) == h, 'Changed final output '+p)
        done = read(OUT/'completion.json')
        need(done['program_complete'] and sha(OUT/'verification.json') == done['verification_sha256'], 'Incomplete terminal state')
        print(json.dumps(done, ensure_ascii=False, indent=2))
        return
    from . import contract as inventory, tests, replay, score, summarize, verify
    functions = {'P0': inventory.run, 'P1': tests.run, 'P2': replay.run,
                 'P3': score.run, 'P4': summarize.run, 'P5': verify.run}
    stages = list(functions) if args.stage == 'all' else [args.stage]
    try:
        for name in stages:
            done = OUT/'stages'/f'{name}.json'
            if done.exists():
                need(args.resume, 'Use --resume to reuse completed stages')
                c = contract()
                for p, h in c['source_sha256'].items():
                    need(sha(ROOT/p) == h, 'Code incompatible with resume')
                need(read(done)['complete'], 'Invalid completed stage')
                print(name+'_already_complete', flush=True)
                continue
            functions[name]()
    except Exception as exc:
        if (OUT/'seal.json').exists():
            pending = [n for n in functions if not (OUT/'stages'/f'{n}.json').exists()]
            write(OUT/f'stop-record-{time.time_ns()}.json', {'reason': repr(exc), 'pending_stages': pending,
                                                          'budget_stop': isinstance(exc, BudgetStop),
                                                          'new_training_authorized': False})
            if not (OUT/'completion.json').exists():
                write(OUT/'completion.json', {'program_complete': False, 'numeric_pass': None,
                                              'source_integrity_pass': None, 'pending_stages': pending,
                                              'status': 'budget_pending' if isinstance(exc, BudgetStop) else 'stopped',
                                              'new_model_fits': 0, 'actual_H_read': False, 'actual_U_read': False,
                                              'new_G_training_authorized': False, 'business_training_authorized': False,
                                              'old_artifacts_changed': False})
        raise


if __name__ == '__main__':
    main()
