"""Collect a bounded, immutable supplement; never changes the original source lock."""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mihomo_protocol_audit'))
from collect_sources import get, HISTORICAL, ROOT

OUT = ROOT / 'outputs/mechanism-guided-drift-20261003/registry/source-supplement'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tree_url = f'https://api.github.com/repos/RakuLomis/mihomo/git/trees/{HISTORICAL}?recursive=1'
    tree = json.loads(get(tree_url))
    assert not tree.get('truncated') and tree['sha'] == HISTORICAL
    paths = [v['path'] for v in tree['tree'] if v['type'] == 'blob' and
             v['path'].endswith('.go') and
             ('semantic' in v['path'].lower() or 'traffictrace' in v['path'].lower())]
    assert len(paths) <= 80, 'Unexpected instrumentation source expansion'
    records = []
    for path in paths:
        url = f'https://raw.githubusercontent.com/RakuLomis/mihomo/{HISTORICAL}/{path}'
        data = get(url)
        destination = OUT / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        records.append({'source_path': path, 'url': url, 'sha256': hashlib.sha256(data).hexdigest(),
                        'local_path': destination.relative_to(ROOT).as_posix()})
    (OUT / 'manifest.json').write_text(json.dumps({'commit': HISTORICAL, 'tree_url': tree_url,
        'sources': records, 'original_source_manifest_modified': False}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(records), 'source_paths': paths}, indent=2))


if __name__ == '__main__':
    main()
