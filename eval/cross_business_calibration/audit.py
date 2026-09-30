"""Audit generated training artifacts without opening evaluation/reference packages."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.cross_business_calibration.common import *

def main():
    for p,h in read(OUT/'contract.json')['inputs'].items():assert sha(p)==h
    for p,h in read(OUT/'worker-contract.json')['files'].items():assert sha(p)==h
    roles=pd.read_parquet(OUT/'roles.parquet');rows=[];supports=[];errors=[]
    for kind in ['paired','group']:
      for folder in sorted((OUT/'generation'/kind).iterdir()):
        done=read(folder/'complete.json');meta=read(OUT/'bundles'/kind/folder.name/'manifest.json')
        assert done['bundle_hash']==sha(OUT/'bundles'/kind/folder.name/'manifest.json')
        for p,h in done['files'].items():assert sha(p)==h
        loco=read(folder/'loco-audit.json')
        for arm,aa in loco.items():
            assert len(aa)==6
            for a in aa:assert set(a['fit_contents'])==set(meta['C_contents'])-{a['held_content']}
            pool=pd.read_parquet(folder/(arm+'-pool.parquet'));assert set(pool.content_id)==set(meta['C_contents'])
            if kind=='paired':
                assert len(pool)==24 and set(pool.session_id)==set(meta['C_sessions'])==set(pool.target_session_id)
                if arm=='X4':assert (pool.session_id==pool.target_session_id).all()
                else:
                    assert (pool.session_id!=pool.target_session_id).all()
                    lookup=pool.set_index('session_id').content_id
                    assert (pool.target_session_id.map(lookup).to_numpy()==pool.content_id.to_numpy()).all()
            else:
                assert len(pool)==96 and pool.groupby('content_id').size().eq(16).all()
                assert not {'session_id','target_session_id','repetition','F'}&set(pool.columns)
                assert not pool.duplicated(['content_id','pre_local_index','post_local_index']).any()
            for c,g in pool.groupby('content_id'):
                v=g[['residual_'+k for k in FEATURES]].to_numpy()
                errors.append({'scenario':folder.name,'protocol':meta['protocol'],'business_group':meta['business_group'],'rotation':meta['rotation'],'arm':arm,'content_id':c,'mean_squared_log_residual':float(np.square(v).sum(1).mean()),'residual_rows':len(g)})
        source=pd.read_parquet(folder/'query-support.parquet');source['kind']=kind;supports.append(source)
        for path in folder.glob('samples-*.parquet'):
            f=pd.read_parquet(path)
            assert set(f.content_id)==set(meta['U_contents']) and not set(f.donor_content.dropna())-set(meta['C_contents'])
            assert f.groupby(['session_id','arm']).view.nunique().eq(8).all()
            values=f[NUMERIC].to_numpy(float);assert np.isfinite(values).all() and (values>=0).all() and (values==np.rint(values)).all()
            U=values[:,:2];E=values[:,2:4];R=values[:,4:6];F=values[:,6]
            assert (R<=E).all() and (E<=U).all() and (R.sum(1)>=F).all() and (abs(R[:,0]-R[:,1])<=F).all()
            assert not (((U==0)&((E!=0)|(R!=0)))|((U>0)&((E<1)|(R<1)))).any()
        rows.append({'scenario':folder.name,'kind':kind,'ridge_fits':done['ridge_fits'],'seconds':done['seconds'],'passed':True})
    a=save('final-generation-audit',rows);assert len(a)==480 and a.ridge_fits.sum()==5040
    support=pd.concat(supports).merge(roles[roles.role=='U'][['scenario','session_id','business_role','label_id','protocol','business_group']],on=['scenario','session_id'],validate='many_to_one')
    save('query-support',support);save('loco-errors',errors)
    write(OUT/'generation-audit.json',{'passed':True,'workers':480,'ridge_fits':5040,'cuda':True,'generated_views':2073600,'source_inputs_unchanged':True,'evaluation_and_reference_opened':False})
    summary=support.groupby(['protocol','business_group','kind','business_role']).agg(queries=('session_id','size'),mean_outside_dimensions=('outside_C_range_dimensions','mean'),mean_nearest_distance=('nearest_C_centroid_distance','mean')).reset_index()
    (DOC/'support-and-audit.md').write_text('# 训练侧支持与谱系审计\n\n'+table(summary)+'\n\n以上是C坐标中的U_pre描述，不使用U_post，不据此筛选或调参。所有donor、LOCO、组级笛卡尔积、24/96行权重与合法摘要核对通过。原始冻结输入哈希未改变。LOCO误差保存在loco-errors.parquet；X6组合误差不等于真实对应恢复误差，不与X4直接当同一目标比较。\n',encoding='utf-8')
    print('480 workers and 2,073,600 outputs audited; no test/reference access',flush=True)

if __name__=='__main__':main()
