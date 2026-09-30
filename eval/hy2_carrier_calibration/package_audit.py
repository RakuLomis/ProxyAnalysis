"""Post-seal fidelity check against measured summaries, not a fitting routine."""
from experiment import *

def main():
    assert read(OUT/'restricted-prediction-seal.json')['passed']
    assert read(OUT/'reference-prediction-seal.json')['passed']
    r=pd.read_parquet(OUT/'roles.parquet');s=pd.read_parquet(OUT/'side-summaries.parquet')
    checks=[]
    for name,roles in r.groupby('scenario'):
        def expected(role,side):
            return roles[roles.role==role][['session_id','content_id','repetition']].merge(s[s.side==side][['session_id',*FEATURES]],on='session_id',validate='one_to_one')
        for kind in ['paired','group']:
            bundle=Bundle(OUT/'bundles'/kind/name,kind)
            for file,role,side in [('C_pre','C','pre'),('C_post','C','post'),('U_pre','U','pre')]:
                actual=bundle.get(file);want=expected(role,side)
                if kind=='group' and role=='C':want=want[['content_id',*FEATURES]]
                assert set(actual)==set(want)
                columns=sorted(actual.columns);order=['content_id',*FEATURES] if kind=='group' and role=='C' else ['session_id']
                pd.testing.assert_frame_equal(actual[columns].sort_values(order).reset_index(drop=True),want[columns].sort_values(order).reset_index(drop=True),check_dtype=False)
            checks.append({'scenario':name,'package':kind,'passed':True})
        for folder,file,role in [('evaluation','H_post','H'),('reference','U_post','U')]:
            actual=pd.read_parquet(OUT/folder/name/(file+'.parquet'));want=expected(role,'post')
            assert set(actual)==set(want) and 'label_id' not in actual
            cols=sorted(actual.columns)
            pd.testing.assert_frame_equal(actual[cols].sort_values('session_id').reset_index(drop=True),want[cols].sort_values('session_id').reset_index(drop=True),check_dtype=False)
            checks.append({'scenario':name,'package':folder,'passed':True})
    save('package-fidelity-audit',checks)
    write(OUT/'package-fidelity.json',{'passed':True,'checked_packages':len(checks),'fitting_performed':False,'script_hash':sha(__file__)})
    print('package fidelity passed',len(checks),flush=True)

if __name__=='__main__':main()
