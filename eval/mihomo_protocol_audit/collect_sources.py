"""Collect immutable source evidence for a read-only protocol/model review."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent / 'mihomo'
OUT = ROOT / 'outputs/mihomo-protocol-audit-20261003'
CURRENT = '88dcbf7f1614a67c3b36b848ee3592dfa92ada36'
HISTORICAL = '74cfed919c03f07a21b252328fe48b72c5361215'
LOCAL = ['go.mod'] + [f'adapter/outbound/{p}.go' for p in
    ['shadowsocks', 'vless', 'vmess', 'trojan', 'anytls', 'hysteria2']] + [
    'transport/vless/conn.go', 'transport/vless/vless.go', 'transport/vless/addons.go',
    'transport/vless/vision/vision.go', 'transport/vless/vision/conn.go',
    'transport/vless/vision/filter.go', 'transport/vless/vision/padding.go',
    'transport/trojan/trojan.go', 'transport/vmess/tls.go',
    'transport/anytls/client.go', 'transport/anytls/padding/padding.go',
    'transport/anytls/session/client.go', 'transport/anytls/session/session.go',
    'transport/anytls/session/frame.go', 'transport/anytls/session/stream.go',
    'transport/shadowsocks/shadowaead/stream.go']
DEPS = {
    'sing-shadowsocks2': ('v0.2.8', ['shadowsocks.go', 'cipher/method_registry.go',
        'shadowaead/method.go', 'shadowaead/protocol.go', 'shadowaead_2022/method.go',
        'shadowaead_2022/protocol.go', 'shadowstream/method.go',
        'internal/shadowio/common.go', 'internal/shadowio/reader.go', 'internal/shadowio/writer.go']),
    'sing-vmess': ('v0.2.5', ['client.go', 'chunk_stream.go', 'chunk_aead.go',
        'chunk_length_stream.go', 'protocol.go', 'aead.go']),
    'sing-quic': ('1c242664697a', ['hysteria2/client.go', 'hysteria2/client_packet.go',
        'hysteria2/protocol.go', 'hysteria2/internal/protocol/proxy.go',
        'hysteria2/internal/protocol/http.go', 'hysteria2/internal/protocol/padding.go',
        'hysteria2/congestion.go', 'hysteria2/salamander.go']),
}
HISTORICAL_DEPS = {'sing-shadowsocks2': 'v0.2.2',
                   'sing-vmess': 'abc39e113b82', 'sing-quic': '2a19cce83925'}


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'ProxyAnalysis-Source-Audit'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise


def save(label, path, data, url=None):
    dest = OUT / label / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {'scope': label, 'source_path': path, 'sha256': hashlib.sha256(data).hexdigest(),
            'local_path': str(dest.relative_to(ROOT)), 'url': url,
            'lines': len(data.decode('utf-8').splitlines())}


def main():
    git = ['git', '-C', str(REPO), '-c', f'safe.directory={REPO.as_posix()}']
    branch = subprocess.check_output(git + ['branch', '--show-current'], text=True).strip()
    before = subprocess.check_output(git + ['status', '--porcelain'])
    assert subprocess.check_output(git + ['rev-parse', 'origin/Meta'], text=True).strip() == CURRENT
    records = []
    for path in LOCAL:
        data = subprocess.check_output(git + ['show', f'{CURRENT}:{path}'])
        records.append(save('current-meta', path, data))
    tasks = []
    dep_versions = {}
    dependency_jobs = [(name, name, ref, paths) for name, (ref, paths) in DEPS.items()]
    dependency_jobs += [('captured-' + name, name, ref, DEPS[name][1])
                        for name, ref in HISTORICAL_DEPS.items()]
    for label, name, ref, paths in dependency_jobs:
        tree = json.loads(get(f'https://api.github.com/repos/MetaCubeX/{name}/git/trees/{ref}?recursive=1'))
        sha = tree['sha']; dep_versions[label] = {'ref': ref, 'commit': sha}
        available = {v['path'] for v in tree['tree']}
        # Preserve all requested files that actually exist, plus source names for later routing.
        save(label, 'source-tree.json', json.dumps(tree, indent=2).encode())
        for path in paths:
            if path in available:
                tasks.append((label, path, f'https://raw.githubusercontent.com/MetaCubeX/{name}/{sha}/{path}'))
    for path in ['go.mod', 'adapter/outbound/shadowsocks.go', 'adapter/outbound/vmess.go',
                 'adapter/outbound/vless.go', 'adapter/outbound/trojan.go',
                 'adapter/outbound/anytls.go', 'adapter/outbound/hysteria2.go',
                 'transport/anytls/client.go', 'transport/anytls/session/client.go',
                 'transport/anytls/session/session.go', 'transport/anytls/padding/padding.go',
                 'transport/vless/conn.go', 'transport/vless/vision/conn.go',
                 'transport/vless/vision/filter.go', 'transport/vless/vision/padding.go',
                 'transport/trojan/trojan.go']:
        tasks.append(('captured-build', path, f'https://raw.githubusercontent.com/RakuLomis/mihomo/{HISTORICAL}/{path}'))
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(get, url): (label, path, url) for label, path, url in tasks}
        for future in concurrent.futures.as_completed(futures):
            label, path, url = futures[future]
            try:
                records.append(save(label, path, future.result(), url))
            except Exception as exc:
                errors.append({'scope': label, 'path': path, 'url': url, 'error': str(exc)})
    assert subprocess.check_output(git + ['status', '--porcelain']) == before
    assert subprocess.check_output(git + ['branch', '--show-current'], text=True).strip() == branch
    manifest = {'date': '2026-10-03', 'local_worktree_branch': branch,
                'meta_commit': CURRENT, 'captured_build_commit': HISTORICAL,
                'dependencies': dep_versions, 'sources': sorted(records, key=lambda r:(r['scope'],r['source_path'])),
                'errors': errors, 'repository_unchanged': True, 'training_performed': False}
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'sources': len(records), 'dependencies': dep_versions, 'errors': errors,
                      'repository_unchanged': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
