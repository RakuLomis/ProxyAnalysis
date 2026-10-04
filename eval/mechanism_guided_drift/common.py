"""Small read-only evidence helpers with Windows long-path support."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/mechanism-guided-drift-20261003/registry'
DOC = ROOT / 'docs/mechanism-guided-drift'
RAW = ROOT / 'Datasets/extend'
OLD = ROOT / 'outputs/extend-calibration-20260930/run-01'
LATEST = ROOT / 'outputs/business-protocol-eval-extend/run-01'
SOURCE = ROOT / 'outputs/mihomo-protocol-audit-20261003'


def long_path(path):
    path = Path(path).absolute()
    text = str(path)
    return Path('\\\\?\\' + text) if os.name == 'nt' and not text.startswith('\\\\?\\') else path


def relative_child(root, relative):
    value = str(relative).replace('\\', '/')
    parts = PurePosixPath(value)
    if parts.is_absolute() or '..' in parts.parts or ':' in value:
        raise ValueError('unsafe_relative_metadata_path')
    return long_path(root).joinpath(*parts.parts)


def read_json(path):
    path = long_path(path)
    if path.suffix.lower() != '.json':
        raise ValueError('json_metadata_only')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def file_hash(path):
    path = long_path(path)
    if path.suffix.lower() in {'.pcap', '.pcapng', '.cap'}:
        raise ValueError('capture_payload_reads_prohibited')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path = long_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), '-c', f'safe.directory={ROOT.as_posix()}', *args], text=True).strip()


def safe_hash(value, length=64):
    import re
    value = value.removeprefix('sha256:') if isinstance(value, str) else ''
    return value if re.fullmatch('[0-9a-f]{' + str(length) + '}', value) else None
