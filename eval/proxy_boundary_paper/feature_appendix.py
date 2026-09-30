"""Export the existing representation definition, without importing training code."""
import ast
import hashlib
import json
import yaml
import build_all as b

path=b.ROOT/'src/proxy_analysis/paired_information/reference_retrain.py'
tree=ast.parse(path.read_text(encoding='utf-8'))
names=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCALAR_NAMES' for t in n.targets))
assert len(names)==14
cfgpath=b.ROOT/'configs/feature-defaults.yaml'
cfg=yaml.safe_load(cfgpath.read_text(encoding='utf-8'))
rows=[[str(i),name.replace('_',r'\_')] for i,name in enumerate(names)]
b.table('scalar_dictionary',['Index','Scalar feature'],rows,'rl')
payload={'scalar14':names,'length_bins':cfg['histograms']['transport_payload_len_edges_bytes'],'iat_edges_us':cfg['histograms']['iat_edges_us'],'curve':cfg['cumulative_shape'],'sources':{str(p.relative_to(b.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,cfgpath,b.ROOT/'src/proxy_analysis/crosscontent/business_representations.py',b.ROOT/'src/proxy_analysis/crosscontent/group_anchor_reliability.py']}}
(b.EVIDENCE/'feature_contract.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print('Feature dictionary exported from existing code/config.')
