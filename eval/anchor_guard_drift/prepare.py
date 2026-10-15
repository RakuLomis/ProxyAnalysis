"""Trusted C-only packer; fit, forecast and score packages are separate."""
from common import *
from anchors import validate_hist

def run():
    with stage('prepare'):
        entries={};audits=[];replay=[]
        def pack(d,p,kind,tokens):
            save(d,p);entries[rel(p)]={'kind':kind,'sha256':sha(p),'columns':list(d),'rows':len(d),'content_tokens':sorted(set(tokens))}
        def numeric(d,side=None):
            cols=HIST if side is None else [side+'_'+h for h in HIST]
            return d[cols].rename(columns=dict(zip(cols,HIST))).reset_index(drop=True)
        def paired(d):
            o=d[['content_token','fit_mass',*['pre_'+h for h in HIST],*['post_'+h for h in HIST]]].copy()
            o.insert(1,'query_key',[hashlib.sha256(('ag-p-query:'+u).encode()).hexdigest() for u in d.visit_id]);return o
        for ri,r in enumerate(contract()['roles']):
            root=rolepath(r);p=parent_package(ROOT/r['C_paired'],'trusted-C-source-packer')
            gp=parent_package(ROOT/r['C_group_pre'],'trusted-C-source-packer');gb=parent_package(ROOT/r['C_group_post'],'trusted-C-source-packer')
            require(set(gp)==set(gb)=={'content_token','fit_mass',*HIST},'Parent anonymous schema')
            allowed={token(u) for u in r['C_contents']}
            for d in [p,gp,gb]:
                require(len(d)==64 and set(d.content_token)==allowed and d.groupby('content_token').size().eq(4).all(),'C member scope')
            a=tensor(p[['pre_'+h for h in HIST]]);b=tensor(p[['post_'+h for h in HIST]])
            validate_hist(a);validate_hist(b)
            for side,gd in [('pre',gp),('post',gb)]:
                for u in allowed:
                    x=numeric(p[p.content_token.eq(u)],side).sort_values(HIST).to_numpy()
                    y=gd[gd.content_token.eq(u)][HIST].sort_values(HIST).to_numpy()
                    require(np.max(np.abs(x-y))<=1e-14,'C paired/group raw frequency replay')
                    replay.append(float(np.max(np.abs(x-y))))
            source=parent_package(PREP/'packages'/r['id']/'source-post.parquet','trusted-C-source-packer')
            pre=parent_package(PREP/'packages'/r['id']/'source-pre.parquet','trusted-C-source-packer')
            for d in [source,pre]:
                require(len(d)==288 and set(d.content_id)<=set(r['train_contents']) and set(d.protocol)==set(r['sources']),'Source scope')
                validate_hist(tensor(d[HIST]))
            require('visit_id' not in pre,'Source pre identities are forbidden')
            old=artifact(ROOT/r['reuse_views'],'trusted-view-packer')
            mu=old['mu'];scale=old['scale'];px=(tensor(pre[HIST])-mu)/scale
            for arm in ['P','G']:
                m=artifact(ROOT/r['reuse_maps'][arm],'trusted-map-packer')
                require(torch.equal(m['mu'],mu) and torch.equal(m['scale'],scale),'Frozen map coordinates')
                err=float((px@m['matrix'].T+m['bias']-old[arm+'_x']).abs().max())
                require(err<1e-12,'Parent mapped source view replay');replay.append(err)
            rawp=pre[HIST].copy().reset_index(drop=True)
            rawp.insert(0,'content_token',[token(u) for u in pre.content_id])
            pack(rawp,root/'source-pre.parquet','source-pre',rawp.content_token)
            put({'mu':mu,'scale':scale},root/'frozen-scaler.pt',role_id=r['id'])
            pp=paired(p);pp.fit_mass=1/64
            pack(pp,root/'full/P.parquet','P-full',allowed)
            rng=np.random.default_rng(20261012+ri)
            for side,d in [('pre',gp),('post',gb)]:
                z=d.iloc[rng.permutation(64)].reset_index(drop=True).copy();z.fit_mass=1/64
                pack(z,root/'full'/f'G-{side}.parquet',f'G-{side}-full',allowed)
            for i,held in enumerate(r['C_diagnostic_contents']):
                val={token(u) for u in held};train=allowed-val;dest=root/f'i{i}'
                pf=pp[pp.content_token.isin(train)].copy().reset_index(drop=True);pf.fit_mass=1/48
                pq=pp[pp.content_token.isin(val)][['content_token','query_key',*['pre_'+h for h in HIST]]].copy()
                pq=pq.rename(columns={'pre_'+h:h for h in HIST}).reset_index(drop=True)
                ps=pp[pp.content_token.isin(val)][['content_token','query_key',*['post_'+h for h in HIST]]].copy()
                ps=ps.rename(columns={'post_'+h:h for h in HIST}).reset_index(drop=True)
                pack(pf,dest/'P-fit.parquet','P-train',train);pack(pq,dest/'P-query.parquet','P-query',val);pack(ps,dest/'P-score.parquet','P-score',val)
                gtrain={}
                for side,d in [('pre',gp),('post',gb)]:
                    df=d[d.content_token.isin(train)].reset_index(drop=True).copy();df=df.iloc[rng.permutation(48)].reset_index(drop=True);df.fit_mass=1/48
                    gtrain[side]=df;pack(df,dest/f'G-{side}-fit.parquet',f'G-{side}-train',train)
                    dv=d[d.content_token.isin(val)].reset_index(drop=True).copy();dv=dv.iloc[rng.permutation(16)].reset_index(drop=True)
                    dv=dv.drop(columns='fit_mass');dv.insert(1,'query_key',[hashlib.sha256(f'ag-g-{ri}-{i}-{side}-{k}'.encode()).hexdigest() for k in range(16)])
                    pack(dv,dest/f'G-{side}-validation.parquet','G-query' if side=='pre' else 'G-score',val)
                sf=source[~source.content_id.isin(held)].reset_index(drop=True)
                require(len(sf)==240 and not set(sf.content_id)&set(held),'Source content holdout scope')
                zz=torch.cat([tensor(sf[HIST]),tensor(gtrain['post'][HIST])]);mn=zz.mean(0);sd=zz.std(0,unbiased=False);sd=torch.where(sd>0,sd,torch.ones_like(sd))
                put({'mu':mn,'scale':sd},dest/'scaler.pt',source_post_rows=240,C_post_rows=48,validation_post_used=False)
                audits.append({'role_id':r['id'],'inner':i,'fit_contents':12,'score_contents':4,'C_fit':48,'C_score':16,'source_scaler_rows':240,
                               'validation_tokens':sorted(val),'training_tokens':sorted(train),'source_held_contents_excluded':True})
            if (ri+1)%12==0:progress('C_source_packing',roles=ri+1,total=60)
        write(OUT/'packages/index.json',entries);write(OUT/'packages/complete.json',{'index_sha256':sha(OUT/'packages/index.json'),'packages':len(entries)})
        save(pd.DataFrame(audits),OUT/'audits/C-splits.parquet')
        write(OUT/'audits/cohort-and-replay.json',{'visits':480,'contents':30,'pairs':23566,'roles':60,'C_folds':240,
              'max_frequency_or_mapped_view_replay_error':max(replay),'full_native_cache_loaded':False,'H_query_packages_read':0,
              'H_label_packages_read':0,'target_U_packages_read':0,'classifier_fits':0,'physical_post_input_qualified':False})

if __name__=='__main__':run()
