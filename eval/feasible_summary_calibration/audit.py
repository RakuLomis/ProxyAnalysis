"""Independent feasibility, lineage, replay and unchanged-source audit."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.feasible_summary_calibration.common import *
from proxy_analysis.feasible_summary_calibration.model import decode,torch,device

def main():
    for p,h in read(OUT/'contract.json')['files'].items():assert sha(p)==h
    for p,h in read(SOURCE/'contract.json')['inputs'].items():assert sha(p)==h
    roles=pd.read_parquet(SOURCE/'roles.parquet',filters=[('role','==','U')],columns=['scenario','session_id','label_id','business_role'])
    rows=[];distribution=[];diversity=[];total=0
    for kind in ['paired','group']:
      for folder in sorted((OUT/'generation'/kind).iterdir()):
        meta=read(SOURCE/'bundles'/kind/folder.name/'manifest.json');done=read(folder/'complete.json')
        assert set(done['read_roles'])==({'C_pre','C_post','U_pre'} if kind=='paired' else {'G_pre','G_post','U_pre'})
        for p,h in done['files'].items():assert sha(p)==h
        for arm,audit in read(folder/'loco.json').items():
            assert len(audit)==6
            for item in audit:assert set(item['fit_contents'])==set(meta['C_contents'])-{item['held_content']}
            pool=pd.read_parquet(folder/(arm+'-pool.parquet'));assert set(pool.content_id)==set(meta['C_contents'])
            if kind=='group':
                assert len(pool)==96 and not {'session_id','target_session_id','F','repetition'}&set(pool.columns)
                assert pool.groupby('content_id').size().eq(16).all()
            else:
                assert set(pool.session_id)==set(meta['C_sessions'])==set(pool.target_session_id)
                if arm=='paired':assert (pool.session_id==pool.target_session_id).all()
                else:
                    assert (pool.session_id!=pool.target_session_id).all()
                    lookup=pool.set_index('session_id').content_id;assert (pool.target_session_id.map(lookup)==pool.content_id).all()
        for path in folder.glob('samples-*.parquet'):
            f=pd.read_parquet(path);assert 'label_id' not in f and set(f.content_id)==set(meta['U_contents'])
            assert not set(f.donor_content.dropna())-set(meta['C_contents'])
            replay,log=decode(f[[f'z{j}' for j in range(6)]].to_numpy(),f.F.to_numpy());np.testing.assert_array_equal(replay.cpu().numpy(),f[FEATURES].to_numpy())
            for k,v in log.items():np.testing.assert_array_equal(v.cpu().numpy(),f[k].to_numpy())
            f=f.merge(roles,on=['scenario','session_id'],validate='many_to_one');total+=len(f)
            for key,g in f.groupby(['protocol','business_group','arm','business_role']):
                ids=dict(zip(['protocol','business_group','arm','business_role'],key))
                for feature in FEATURES:
                    v=g[feature].to_numpy();distribution.append({**ids,'scenario':folder.name,'seed':int(g.seed.iloc[0]),'feature':feature,'min':int(v.min()),'q05':float(np.quantile(v,.05)),'median':float(np.quantile(v,.5)),'q95':float(np.quantile(v,.95)),'max':int(v.max())})
            for (sid,arm),g in f.groupby(['session_id','arm']):
                diversity.append({'scenario':folder.name,'protocol':g.protocol.iloc[0],'business_group':int(g.business_group.iloc[0]),'seed':int(g.seed.iloc[0]),'session_id':sid,'arm':arm,'business_role':g.business_role.iloc[0],'unique_views':len(g[FEATURES].drop_duplicates()),'views':len(g)})
        rows.append({'scenario':folder.name,'kind':kind,'passed':True,'fits':done['fits'],'cuda_decode_replay':True})
    assert total==2073600 and len(rows)==480
    save('generation-lineage-audit',rows);save('generated-distribution',distribution);save('view-diversity',diversity)
    write(OUT/'generation-audit.json',{'passed':True,'workers':480,'views':total,'cuda_decode_replay':True,'old_inputs_unchanged':True,'U_post_opened':False,'evaluation_opened':False,'script_hash':sha(__file__)})
    print('Independent generation audit passed',total,flush=True)

if __name__=='__main__':main()
