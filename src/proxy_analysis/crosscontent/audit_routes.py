"""Supplement capture audit with request routing, redirects and design coverage."""
from collections import Counter, defaultdict
import json
from pathlib import Path
from urllib.parse import urlsplit

from ..reproducibility.registry import read_json
from ..reproducibility.preflight import write_json, write_table
from ..paired_information.prepare import table
from .audit_capture import file_hash


def main():
    root=Path('outputs/content-generalization-20260916/audit-01')
    rows=[r for r in table(root/'run-registry.parquet') if r['is_final']]
    out=root/'routing'
    out.mkdir(exist_ok=False)
    records, sources, proxy_hosts = [], {}, Counter()
    for row in rows:
        path=Path(row['session_path'])
        connection_path=path/'analysis/connection-index-v2.json'
        request_path=path/'analysis/request-index-v2.json'
        for item in (connection_path, request_path): sources[str(item)]=file_hash(item)
        connections={c['connection_id']:c for c in read_json(connection_path)['items']}
        requests=read_json(request_path)['items']
        counts, main, media = Counter(), Counter(), Counter()
        for request in requests:
            c=connections.get(request.get('connection_id'),{})
            outcome=(c.get('egress') or {}).get('outcome','unresolved')
            counts[outcome]+=1
            if request.get('url')==row['target_url']:
                main[outcome]+=1
            if request.get('resource_type','').lower()=='media':
                media[outcome]+=1
            if row['target_domain']=='bilibili.com' and outcome=='proxy':
                proxy_hosts[(row['protocol'],urlsplit(request.get('url','')).hostname)]+=1
        records.append({'session_id':row['session_id'],'domain':row['target_domain'],
            'protocol':row['protocol'],'target_url':row['target_url'],
            'request_route_counts_json':json.dumps(dict(counts)),
            'exact_target_request_route_counts_json':json.dumps(dict(main)),
            'media_type_route_counts_json':json.dumps(dict(media)),
            'proxy_requests':counts['proxy'],'direct_requests':counts['direct'],
            'unresolved_requests':counts['unresolved'],
            'exact_target_proxy':main['proxy']>0,'exact_target_direct':main['direct']>0,
            'exact_target_found':bool(main),
            'page_connections':sum(c.get('attribution_scope')=='page_attributed' for c in connections.values())})
    write_table(out/'session-routing.parquet',records)
    grouped=defaultdict(list)
    for r in records: grouped[(r['domain'],r['protocol'])].append(r)
    summary=[]
    for (domain, protocol), members in sorted(grouped.items()):
        summary.append({'domain':domain,'protocol':protocol,'sessions':len(members),
            'sessions_with_proxy_requests':sum(r['proxy_requests']>0 for r in members),
            'sessions_with_direct_requests':sum(r['direct_requests']>0 for r in members),
            'sessions_with_unresolved_requests':sum(r['unresolved_requests']>0 for r in members),
            'exact_target_proxy_sessions':sum(r['exact_target_proxy'] for r in members),
            'exact_target_direct_sessions':sum(r['exact_target_direct'] for r in members),
            'exact_target_not_found':sum(not r['exact_target_found'] for r in members)})
    write_json(out/'route-summary.json',summary)
    write_json(out/'sources.json',sources)
    write_json(out/'bilibili-proxy-request-hosts.json',[{'protocol':p,'host':h,'requests':n} for (p,h),n in proxy_hosts.most_common()])
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    print(json.dumps({'bilibili_proxy_hosts':[{'protocol':p,'host':h,'requests':n} for (p,h),n in proxy_hosts.most_common()]},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
