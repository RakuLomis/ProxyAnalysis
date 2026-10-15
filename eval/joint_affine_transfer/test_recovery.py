"""Recovery safety tests without fitting or opening experiment packages."""
import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import recover


POLICY = dict(objective_slack=1e-10, original_gradient_max=1e-5, max_iter=2000,
              objective_replay_tolerance=1e-10, gradient_replay_tolerance=1e-10)
GOOD = {'optimizer': dict(accepted=True, device='cuda:0', dtype='float64',
                         numeric_policy_sha256='seal', objective=1., initial_objective=2.,
                         max_gradient=9e-6, iterations=1999, objective_replay_error=0.,
                         gradient_replay_error=0.)}


class RecoveryTests(unittest.TestCase):
    def test_original_gates(self):
        recover.gate_model(GOOD, POLICY, 'seal')
        changes = dict(accepted=False, device='cpu', dtype='float32', numeric_policy_sha256='other',
                       objective=3., max_gradient=1.1e-5, iterations=2000,
                       objective_replay_error=1e-10, gradient_replay_error=1e-10)
        for name, value in changes.items():
            with self.subTest(name=name):
                info = copy.deepcopy(GOOD); info['optimizer'][name] = value
                with self.assertRaises(RuntimeError):
                    recover.gate_model(info, POLICY, 'seal')

    def test_live_pid(self):
        self.assertTrue(recover.pid_alive(os.getpid()))

    def test_failure_and_completion_stop_before_any_input_read(self):
        for marker in ['failure.json', 'completion.json']:
            with tempfile.TemporaryDirectory() as tmp:
                run = Path(tmp).resolve(); (run / marker).touch()
                with patch.object(recover, 'DEFAULT', run):
                    with self.assertRaises(RuntimeError):
                        recover.preflight(run)

    def test_live_lock_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp).resolve(); lock = run / 'runner.lock'
            lock.write_text(str(os.getpid()))
            with patch.object(recover, 'DEFAULT', run):
                with self.assertRaises(RuntimeError):
                    recover.preflight(run)
            self.assertEqual(lock.read_text(), str(os.getpid()))

    def test_other_worker_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp).resolve()
            with patch.object(recover, 'DEFAULT', run), patch.object(recover, 'workers', return_value=[123]):
                with self.assertRaises(RuntimeError):
                    recover.preflight(run)

    def test_wrong_scope(self):
        with self.assertRaises(RuntimeError):
            recover.preflight(Path('C:/Windows').resolve())


if __name__ == '__main__':
    unittest.main()
