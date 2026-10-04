"""Explicit data capabilities for training, generation, inference and scoring."""
import pandas as pd
from common import *

ALLOWED = {
    'M0': {'post'}, 'I0': {'post'}, 'M1': {'post','pre_unpaired'},
    'M2': {'post'}, 'M3': {'post'}, 'M4': {'post'},
    'paired': {'fit_pre','fit_post','query_pre'},
    'cyclic': {'fit_pre','fit_post','query_pre'},
    'group': {'group_pre','group_post','query_pre'},
    'inference': {'test_post'}, 'scoring': {'test_labels'},
}


class Bundle:
    def __init__(self, folder, capability):
        self.folder=Path(folder);self.capability=capability;self.access=[]
        self.meta=read(self.folder/'manifest.json')

    def get(self, name):
        if name not in ALLOWED[self.capability] or name not in self.meta['files']:
            raise PermissionError(f'{self.capability} cannot read {name}')
        item=self.meta['files'][name];p=self.folder/item['filename']
        assert p.resolve().parent==self.folder.resolve()
        assert file_hash(p)==item['sha256']
        f=pd.read_parquet(p);assert list(f)==item['columns'] and len(f)==item['rows']
        self.access.append(name);return f


def export(folder, frames, meta):
    folder.mkdir(parents=True,exist_ok=True)
    assert not (folder/'manifest.json').exists()
    files={}
    for name,frame in frames.items():
        path=folder/f'{name}.parquet';frame.to_parquet(path,index=False)
        files[name]={'filename':path.name,'columns':list(frame),'rows':len(frame),'sha256':file_hash(path)}
    write(folder/'manifest.json',{**meta,'files':files})


def main():
    assert read(OUT/'gate-A.json')['passed']
    assert not (OUT/'gate-packages.json').exists()
    check_files(read(OUT/'source-lock.json')['inputs'])
    cohort=pd.read_parquet(OUT/'cohort.parquet')
    data=pd.read_parquet(EXTRACT/'full-W-features.parquet')
    sides={s:data[data.side.eq(s)].set_index('session_id') for s in ['pre','post']}
    # Numerically compare reused features against already sealed v3 packages.
    prior=read(EXTRACT/'training-preparation-01/preregistration.json')
    seen={s:set() for s in sides};checks=0
    for p in PROTOCOLS:
        for fold in range(5):
            for kind,names in [('scoring',['H_post']),('paired',['C_pre','U_pre'])]:
                folder=EXTRACT/'training-preparation-01/packages'/kind/f'W-{p}-f{fold}-g0-r0'
                mf=folder/'manifest.json'
                assert file_hash(mf)==prior['package_manifest_hashes'][str(mf.relative_to(ROOT))]
                meta=read(mf)
                for name in names:
                    item=meta['files'][name];path=folder/item['filename'];assert file_hash(path)==item['sha256']
                    f=pd.read_parquet(path);s='post' if name.endswith('post') else 'pre'
                    np.testing.assert_array_equal(f[FEATURES].to_numpy(),sides[s].loc[f.session_id,FEATURES].to_numpy())
                    seen[s].update(f.session_id);checks+=len(f)
    assert all(v==set(cohort.session_id) for v in seen.values())

    def frame(ids,side,fields):
        m=cohort.set_index('session_id').loc[ids].reset_index()
        return m[fields].merge(sides[side][FEATURES],left_on='session_id',right_index=True,validate='one_to_one')

    negative=0
    for path in sorted((OUT/'roles').glob('*.json')):
        role=read(path);name=role['scenario']
        tr=frame(role['train'],'post',['session_id','protocol','content_id','repetition','label_id'])
        pre=frame(role['train'],'pre',['session_id','protocol','content_id','label_id']).drop(columns='session_id')
        # Independent value ordering, no paired visit ID or repetition index.
        pre=pre.sort_values(['protocol','content_id',*FEATURES]).reset_index(drop=True)
        test=frame(role['test'],'post',['session_id'])
        labels=cohort.set_index('session_id').loc[role['test']].reset_index()
        folder=OUT/'packages/training'/name
        export(folder,{'post':tr,'pre_unpaired':pre},{'scenario':name,'source_protocols':role['source_protocols']})
        export(OUT/'packages/inference'/name,{'test_post':test},{'scenario':name})
        export(OUT/'packages/scoring'/name,{'test_labels':labels},{'scenario':name})
        for cap in ['M0','M1','M2','M3','M4','I0']:
            b=Bundle(folder,cap)
            assert set(b.get('post').session_id)==set(role['train'])
            for forbidden in ['test_post','test_labels','target_pre','target_post','H_pre']:
                try:b.get(forbidden)
                except PermissionError:negative+=1
                else:raise AssertionError('Permission escape')
        assert set(pre)=={'protocol','content_id','label_id',*FEATURES}
    for path in sorted((OUT/'generator-roles').glob('*.json')):
        job=read(path);name=job['job']
        fields=['session_id','content_id','repetition']
        pre=frame(job['fit_sessions'],'pre',fields);post=frame(job['fit_sessions'],'post',fields)
        query=frame(job['query_sessions'],'pre',fields)
        export(OUT/'packages/generator-paired'/name,{'fit_pre':pre,'fit_post':post,'query_pre':query},
               {'job':name,'protocol':job['protocol'],'fold':job['fold'],'query_group':job['query_group']})
        anon=lambda f:f[['content_id',*FEATURES]].sort_values(['content_id',*FEATURES]).reset_index(drop=True)
        export(OUT/'packages/generator-group'/name,{'group_pre':anon(pre),'group_post':anon(post),'query_pre':query},
               {'job':name,'protocol':job['protocol'],'fold':job['fold'],'query_group':job['query_group']})
        b=Bundle(OUT/'packages/generator-group'/name,'group')
        assert set(b.get('group_post'))=={'content_id',*FEATURES}
        for forbidden in ['fit_pre','fit_post','labels','query_post','test_post']:
            try:b.get(forbidden)
            except PermissionError:negative+=1
            else:raise AssertionError('Group identity permission escape')
    write(OUT/'gate-packages.json',{'passed':True,'classifier_scenarios':55,'generator_jobs':100,
          'numeric_comparisons_to_v3_rows':checks,'unique_pre_verified':600,'unique_post_verified':600,
          'permission_negative_tests':negative,'test_pre_exported':False,'training_allowed':False,
          'OS_sandbox_claimed':False,'script_sha256':file_hash(Path(__file__))})
    print(read(OUT/'gate-packages.json'))


if __name__=='__main__':main()
