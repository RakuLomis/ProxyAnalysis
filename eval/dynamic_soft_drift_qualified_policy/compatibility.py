"""CUDA read-only replay of all original fallback models and weighted slots."""
from common import *

def run():
    from feedback import FW,legacy
    _,u,_,_=production();rows=[]
    refs={(x['role_id'],x['arm']):x for x in contract()['references']}
    for r in contract()['roles']:
        old=registered_load(ROOT/r['reuse_views'],'combined-baseline-view',r)
        for kind in ['P','G']:
            v=parent_asset(PARENT/'tasks'/r['id']/(kind+'.pt'),'task',kind,r['id'],'compatibility-auditor')['view']
            require('query_x' not in v and len(v['main_x'])==288 and len(v['C_x'])==64,'Outer train-only task')
            for key in ['main_x','main_y','main_mass','S_x','S_y','S_mass','C_x','C_y','C_mass','mu','scale']:require(torch.equal(v[key],old[key]),'Common frozen coordinates/order changed '+key)
            mp=registered_load(ROOT/r['reuse_maps'][kind],'map-'+kind,r);mi=read((ROOT/r['reuse_maps'][kind]).with_suffix('.json'))
            require(mi['eta']==r['eta'] and mi['mapping']['accepted'],'Map eta/qualification')
            require(torch.equal(mp['mu'],v['mu']) and torch.equal(mp['scale'],v['scale']),'Map coordinate mismatch')
            maperr=float((v['pre_x']@mp['matrix'].T+mp['bias']-v['mapped_x']).abs().max());require(maperr<1e-12,'Fixed map replay')
            s=u.pack(v,legacy(kind),tensor(np.ones(10)))
            canonical=dict(x=torch.cat([old['main_x'],old['S_x'],old[kind+'_x'],old['C_x']]),
                           y=torch.cat([old['main_y'],old['S_y'],old[kind+'_y'],old['C_y']]),
                           mass=torch.cat([old['main_mass'],old['S_mass']*.9,old[kind+'_mass']*.1,old['C_mass']]))
            err=float((s['x']-canonical['x']).abs().max());require(err<1e-12 and torch.equal(s['y'],canonical['y']) and torch.equal(s['mass'],canonical['mass']),'q=1 baseline slot changed')
            require(len(s['x'])==928 and abs(float(s['mass'].sum())-1)<1e-12 and float((weighted(s['y'],s['mass'],6)-1/6).abs().max())<1e-12,'Final class mass')
            ref=refs[(r['id'],kind+'-small')];p=ROOT/ref['model_path'];m=registered_load(p,'reference',r);meta=read(p.with_suffix('.json'));log=meta['optimizer']
            require(meta['role_id']==r['id'] and meta['t']==r['t'] and meta['eta']==r['eta'] and meta['beta']==.1,'Baseline settings/members')
            require(log['accepted'] and log['initialization']=='zero' and log['settings']['max_iter']==2000 and log['settings']['max_eval']==10000 and log['solver']==SOLVER,'Baseline numeric policy')
            require(torch.equal(m['mu'],v['mu']) and torch.equal(m['scale'],v['scale']),'Baseline inference coordinates')
            theta=torch.cat([m['weight'],m['bias'][:,None]],1);audit,_=FW.independent(theta,canonical,r['t']);replay,_=FW.independent(theta,s,r['t'])
            require(audit['original_gradient']<=1e-5 and replay['original_gradient']<=1e-5,'Baseline original gradient gate')
            je=abs(audit['J']-log['objective']);require(je<1e-10 and abs(audit['J']-replay['J'])<1e-10,'Baseline objective changed')
            rows.append(dict(role_id=r['id'],outer=r['outer'],target=r['target'],group=r['group'],kind=kind,t=r['t'],eta=r['eta'],slot_rows=928,mapped_mass=float(v['pre_mass'].sum()*.1),slot_max_error=err,map_max_error=maperr,objective_error=je,original_gradient=replay['original_gradient'],model_path=ref['model_path'],model_sha256=ref['model_sha256'],passed=True,new_fit=False))
        if len(rows)%24==0:progress('fallback_replay',models=len(rows),expected=120)
    require(len(rows)==120,'Fallback coverage');save(pd.DataFrame(rows),OUT/'audits/fallback-compatibility.parquet')
    write(OUT/'audits/fallback-compatibility.json',dict(passed=True,models=120,final_rows=928,new_fits=0,H_U_reads=0,maximum_input_error=max(x['slot_max_error'] for x in rows),maximum_objective_error=max(x['objective_error'] for x in rows)))
    for ref in contract()['references']:
        m=registered_load(ROOT/ref['model_path'],'reference');cuda(m['weight'],m['bias'],m['mu'],m['scale'])
        require(m['weight'].shape==(6,96) and bool((m['scale']>0).all()),'Reference shape/scale')
    write(OUT/'audits/reference-integrity.json',dict(passed=True,models=420,new_fits=0))
