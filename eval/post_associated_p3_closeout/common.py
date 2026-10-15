"""P3 seal-only repair. Historical outputs are read-only; never import trainers."""
from pathlib import Path
import hashlib
import json
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'outputs/post-input-associated-representation-20261014/run-01'
SOURCE = ROOT / 'outputs/post-input-associated-representation-20261014/run-02'
OUT = ROOT / 'outputs/post-input-associated-representation-20261014/run-03'
CODE = Path(__file__).resolve().parent
ACCESS = []
SEEDS = [20261014, 20261015, 20261016]


def require(value, message):
    if not value:
        raise RuntimeError(message)


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path, purpose='metadata'):
    ACCESS.append(dict(path=rel(path), sha256=sha(path), purpose=purpose))
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path).resolve()
    require(path.is_relative_to(OUT), 'Write outside repair output')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')


def seal(path, files, **extra):
    write(path, dict(files={rel(p): sha(p) for p in sorted(set(files))}, **extra))


def verifyseal(path):
    record = read(path, 'seal')
    require(record.get('passed', False), 'Source seal not passed')
    for name, digest in record['files'].items():
        require(sha(ROOT / name) == digest, 'Source seal changed: ' + name)
        ACCESS.append(dict(path=name, sha256=digest, purpose='sealed-byte-integrity'))


def history_files():
    paths = []
    for folder in [PARENT, SOURCE,
                   ROOT/'eval/post_input_associated_representation',
                   ROOT/'eval/post_input_associated_representation_v2',
                   ROOT/'eval/post_input_associated_representation_v3']:
        paths.extend(p for p in folder.rglob('*') if p.is_file())
    paths.append(ROOT/'plan/post-input-associated-representation-residual-plan-20261014.md')
    return sorted(set(paths))


def snapshot():
    files = history_files()
    result = {}
    for i, p in enumerate(files, 1):
        result[rel(p)] = sha(p)
        if i % 10000 == 0:
            print('historical_hash_progress', i, len(files), flush=True)
    return result


def collect_model_files(root, endpoints):
    """Correct Path joining, replacing ROOT[e['...']] in historical P3."""
    root = Path(root).resolve()
    paths = {root / e['base_path'] for e in endpoints}
    paths |= {root / e['residual_path'] for e in endpoints if e['residual_path']}
    require(all(p.resolve().is_relative_to(root) for p in paths), 'Model path escapes workspace')
    return paths


def self_tests():
    example = [dict(base_path='outputs/a.pt', residual_path=None),
               dict(base_path='outputs/a.pt', residual_path='outputs/b.pt')]
    require(collect_model_files(ROOT, example) == {ROOT/'outputs/a.pt', ROOT/'outputs/b.pt'}, 'Path join/dedup regression')
    rejected = False
    try:
        collect_model_files(ROOT, [dict(base_path='../outside.pt', residual_path=None)])
    except RuntimeError:
        rejected = True
    require(rejected, 'Path escape negative test')
    return dict(path_join_pass=True, optional_residual_pass=True, dedup_pass=True, escape_rejected=True)
