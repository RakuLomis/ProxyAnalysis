"""Fetch only pinned public implementation evidence; never capture credentials."""
import re
import urllib.request
from .common import *

def sources():
    dest=OUT/'implementation';dest.mkdir(exist_ok=True)
    manifest=[]
    def fetch(repo,commit,path):
        url=f'https://raw.githubusercontent.com/{repo}/{commit}/{path}'
        target=dest/(repo.replace('/','_')+'__'+commit+'__'+path.replace('/','_'))
        try:
            if not target.exists():
                data=urllib.request.urlopen(url,timeout=25).read()
                target.write_bytes(data)
            manifest.append({'url':url,'repository':repo,'commit':commit,'path':path,'local_path':str(target),'sha256':digest(target),'status':'ok'})
            return target.read_text(encoding='utf-8')
        except Exception as exc:
            manifest.append({'url':url,'status':'unavailable','error':str(exc)});return ''
    mod=fetch('MetaCubeX/mihomo',COMMIT,'go.mod')
    fetch('MetaCubeX/mihomo',COMMIT,'adapter/outbound/vless.go')
    for path in ['transport/vless/vless.go','transport/vless/vision.go','transport/vless/conn.go','transport/vmess/tls.go']:
        fetch('MetaCubeX/mihomo',COMMIT,path)
    match=re.search(r'github.com/metacubex/sing-vmess\s+\S+-([0-9a-f]{12})',mod)
    for name in ['conn.go','filter.go','padding.go','vision.go']:
        fetch('MetaCubeX/mihomo',COMMIT,'transport/vless/vision/'+name)
    if match:
        revision=match.group(1)
        # Get exact tree to locate files rather than substituting current source.
        url=f'https://api.github.com/repos/MetaCubeX/sing-vmess/git/trees/{revision}?recursive=1'
        try:
            tree=json.loads(urllib.request.urlopen(url,timeout=25).read())
            js('dependency-tree.json',tree)
            for entry in tree.get('tree',[]):
                path=entry['path']
                if path.endswith('.go') and ('vision' in path.lower() or path in ['vless/client.go','vless/protocol.go']):fetch('MetaCubeX/sing-vmess',revision,path)
        except Exception as exc:manifest.append({'url':url,'status':'unavailable','error':str(exc)})
    js('implementation-sources.json',manifest)
    print('E6 pinned source files:',sum(r['status']=='ok' for r in manifest),flush=True)
