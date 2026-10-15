"""Fixed prediction scoring, 12-comparison bootstrap, descriptions and delivery."""
import sys
from common import *

def outerroles(c): return [r for r in c['roles'] if r['inner'] is None]

def checked_predictions():
    path=OUT/'predictions/visits.parquet'
    require(sha(path)==read(OUT/'predictions/complete.json')['sha256'],'Prediction seal changed')
    return pd.read_parquet(path)

def evaluate():
    c=start('score'); pred=checked_predictions(); labels=[]
    for r in outerroles(c):
        s=package(folder('packages',r['outer'],r['protocol'])/'score-labels.parquet','score')
        labels.append(s)
    label=pd.concat(labels,ignore_index=True)
    require(len(label)==480 and label.visit_id.is_unique,'Test label support changed')
    data=pred.merge(label.drop(columns=['protocol','fold']),on='visit_id',validate='many_to_one')
    data['truth']=truths(data)
    require(len(data)==2400 and data.groupby(['arm','protocol']).size().eq(120).all(),'Final arm coverage changed')
    saveparquet(data,OUT/'scores/scored-visits.parquet'); rows=[]; classes=[]; cms=[]; errors=[]
    for (p,arm),df in data.groupby(['protocol','arm']):
        m,cm=metrics(df.truth.to_numpy(),df[[f'p{i}' for i in range(6)]].to_numpy())
        rows.append({'protocol':p,'arm':arm,'visits':len(df),**m})
        for j,labelname in enumerate(LABELS):
            tp=cm[j,j]; recall=tp/cm[j].sum() if cm[j].sum() else 0
            precision=tp/cm[:,j].sum() if cm[:,j].sum() else 0
            classes.append({'protocol':p,'arm':arm,'label':labelname,'support':int(cm[j].sum()),
                'precision':precision,'recall':recall,'F1':2*precision*recall/(precision+recall) if precision+recall else 0})
            for k in range(6): cms.append({'protocol':p,'arm':arm,'truth':LABELS[j],'predicted':LABELS[k],'count':int(cm[j,k])})
        for content,g in df.groupby('content_id'):
            errors.append({'protocol':p,'arm':arm,'content_id':content,'label':g.label_id.iloc[0],
                           'visits':len(g),'errors':int(g.prediction.ne(g.truth).sum())})
    summary=pd.DataFrame(rows)
    saveparquet(summary,OUT/'scores/protocol-summary.parquet')
    saveparquet(pd.DataFrame(classes),OUT/'scores/class-summary.parquet')
    saveparquet(pd.DataFrame(cms),OUT/'scores/confusion.parquet')
    saveparquet(pd.DataFrame(errors),OUT/'scores/content-errors.parquet')
    globalrows=[]
    for arm,df in data.groupby('arm'):
        m,_=metrics(df.truth.to_numpy(),df[[f'p{i}' for i in range(6)]].to_numpy())
        by=summary[summary.arm.eq(arm)]
        globalrows.append({'arm':arm,'protocol_equal_mean_F1':float(by.F1.mean()),
                            'worst_protocol_F1':float(by.F1.min()),'pooled':m})
    write(OUT/'scores/global-summary.json',globalrows)
    flips=[]; detail=[]
    for p in PROTOCOLS:
        base=data[data.protocol.eq(p)&data.arm.eq('KSR2')].set_index('visit_id')
        for opponent in ['KSR0','KSR1','KSR3','KSR4']:
            other=data[data.protocol.eq(p)&data.arm.eq(opponent)].set_index('visit_id').loc[base.index]
            repaired=base.prediction.eq(base.truth)&other.prediction.ne(other.truth)
            added=base.prediction.ne(base.truth)&other.prediction.eq(other.truth)
            flips.append({'protocol':p,'comparison':'KSR2-'+opponent,'repaired_errors':int(repaired.sum()),
                          'added_errors':int(added.sum()),'changed_predictions':int(base.prediction.ne(other.prediction).sum())})
            for visit in base.index:
                detail.append({'protocol':p,'comparison':'KSR2-'+opponent,'visit_id':visit,
                    'content_id':base.loc[visit,'content_id'],'label':base.loc[visit,'label_id'],
                    'repaired':bool(repaired.loc[visit]),'added':bool(added.loc[visit])})
    saveparquet(pd.DataFrame(flips),OUT/'scores/error-flips.parquet')
    saveparquet(pd.DataFrame(detail),OUT/'scores/error-flip-visits.parquet')
    finish('score',scored_visits=2400,truth_labels_joined_after_prediction_seal=True)
    print(summary.pivot(index='protocol',columns='arm',values='F1').to_string(),flush=True)

def bootstrap_f1(y,pred,mult):
    one=np.eye(36)[y*6+pred]; cm=(mult@one).reshape(-1,6,6)
    tp=np.diagonal(cm,axis1=1,axis2=2); den=cm.sum(1)+cm.sum(2)
    return np.divide(2*tp,den,out=np.zeros_like(tp),where=den>0).mean(1)

def uncertainty():
    c=start('bootstrap'); data=pd.read_parquet(OUT/'scores/scored-visits.parquet')
    contents=data[['content_id','label_id']].drop_duplicates().sort_values(['label_id','content_id']).reset_index(drop=True)
    require(len(contents)==30 and contents.groupby('label_id').size().eq(5).all(),'Bootstrap support wrong')
    rng=np.random.default_rng(c['bootstrap']['seed'])
    ix=np.concatenate([rng.choice(np.arange(5*j,5*j+5),size=(10000,5),replace=True) for j in range(6)],axis=1)
    (OUT/'comparisons').mkdir(exist_ok=True); np.save(OUT/'comparisons/bootstrap-indices.npy',ix)
    counts=np.stack([np.bincount(row,minlength=30) for row in ix]); mapping={u:i for i,u in enumerate(contents.content_id)}
    rows=[]; summaries=pd.read_parquet(OUT/'scores/protocol-summary.parquet').set_index(['protocol','arm'])
    for p in PROTOCOLS:
        boot={}
        for arm in ARMS:
            df=data[data.protocol.eq(p)&data.arm.eq(arm)].sort_values('visit_id')
            boot[arm]=bootstrap_f1(df.truth.to_numpy(),df.prediction.to_numpy(),counts[:,df.content_id.map(mapping).to_numpy()])
        for other in ['KSR1','KSR3','KSR4']:
            delta=boot['KSR2']-boot[other]; q=np.quantile(delta,[.025,.975,c['bootstrap']['tail'],1-c['bootstrap']['tail']])
            rows.append({'protocol':p,'comparison':'KSR2-'+other,
                'point':float(summaries.loc[(p,'KSR2'),'F1']-summaries.loc[(p,other),'F1']),
                'lo95':float(q[0]),'hi95':float(q[1]),'family_lo':float(q[2]),'family_hi':float(q[3]),
                'family_positive':bool(q[2]>0),'family_negative':bool(q[3]<0),'family_size':12})
        print('10000 content bootstrap',p,flush=True)
    saveparquet(pd.DataFrame(rows),OUT/'comparisons/F1-contrasts.parquet')
    saveparquet(contents,OUT/'comparisons/bootstrap-content-order.parquet')
    write(OUT/'comparisons/complete.json',{'index_sha256':sha(OUT/'comparisons/bootstrap-indices.npy'),
        'order_sha256':sha(OUT/'comparisons/bootstrap-content-order.parquet'),
        'comparisons_sha256':sha(OUT/'comparisons/F1-contrasts.parquet'),
        'ordinary_coverage':.95,'Bonferroni_marginal_coverage':1-.05/12,
        'fixed_selected_model_conditional':True,'nested_retraining_bootstrap':False,'family_size':12})
    finish('bootstrap',main_comparisons=12,samples=10000)

def explain():
    c=start('explain'); energies=[]; weightrows=[]; spectral=[]; blockrows=[]
    choices={(x['outer'],x['protocol'],x['arm']):x['t'] for x in read(OUT/'selection/choices.json')}
    for r in outerroles(c):
        outer,p=r['outer'],r['protocol']; mf=folder('models',outer,p); rf=folder('regularizers',outer,p)
        summary=read(rf/'summary.json')
        for spec in summary['spectra']:
            for coord in ['raw','normalized']:
                row={k:v for k,v in spec[coord].items() if k!='eigenvalues'}
                spectral.append({'outer':outer,'protocol':p,'arm':spec['arm'],'coordinates':coord,
                    'trace_multiplier':spec['trace_multiplier'],'smoothing_difference_Frobenius':summary['smoothing_difference_Frobenius'],**row})
        for b in summary['blocks']: blockrows.append({'outer':outer,'protocol':p,**b})
        reference=artifact(mf/'zero.pt','explain')
        for arm in ARMS:
            t=0 if arm=='KSR0' else choices[(outer,p,arm)]
            model=artifact(mf/('zero.pt' if t==0 else f'{arm}-t{t:g}.pt'),'explain')
            cw=model['weight']-model['weight'].mean(0,keepdim=True)
            weightrows.append({'outer':outer,'protocol':p,'arm':arm,'t':t,
               'weight_Frobenius':float(torch.linalg.matrix_norm(model['weight'])),
               'baseline_weight_difference':float(torch.linalg.matrix_norm(model['weight']-reference['weight'])),
               'common_class_weight_max':float(model['weight'].mean(0).abs().max())})
            for matrixarm in ['KSR2','KSR3','KSR4']:
                matrix=artifact(rf/(matrixarm+'.pt'),'explain')['normalized_matrix']; at=0
                for j,f in enumerate(FEATURES):
                    k=size(f); block=matrix[at:at+k,at:at+k]; w=cw[:,at:at+k]
                    energy=float((w@block*w).sum()/5)
                    energies.append({'outer':outer,'protocol':p,'classifier_arm':arm,'matrix_arm':matrixarm,
                         'feature':f,'family':'bytes' if j<4 else 'events' if j<8 else 'interaction',
                         'sensitivity':energy,'classifier_t':t})
                    at+=k
    saveparquet(pd.DataFrame(energies),OUT/'explanations/training-sensitivity.parquet')
    saveparquet(pd.DataFrame(weightrows),OUT/'explanations/weight-changes.parquet')
    saveparquet(pd.DataFrame(spectral),OUT/'explanations/matrix-spectra.parquet')
    saveparquet(pd.DataFrame(blockrows),OUT/'explanations/block-traces.parquet')
    selections=pd.DataFrame(read(OUT/'selection/choices.json'))
    frequency=selections.groupby(['protocol','arm','t']).size().rename('roles').reset_index()
    saveparquet(frequency,OUT/'explanations/selection-frequency.parquet')
    finish('explain',test_model_selection=False,weights_and_matrices_training_only=True)

def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    target=OUT/'figures'; target.mkdir(exist_ok=True)
    score=pd.read_parquet(OUT/'scores/protocol-summary.parquet')
    fig,ax=plt.subplots(figsize=(10,4)); x=np.arange(4); width=.15
    for j,arm in enumerate(ARMS):
        v=score[score.arm.eq(arm)].set_index('protocol').loc[PROTOCOLS]
        ax.bar(x+(j-2)*width,v.F1,width,label=arm)
    ax.set(xticks=x,xticklabels=['SS','VLESS','Trojan','VMess'],ylim=(0,1),ylabel='Six-class macro F1')
    ax.legend(ncol=5,fontsize=8); fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(target/f'protocol-F1.{ext}',dpi=180)
    plt.close(fig)
    contrast=pd.read_parquet(OUT/'comparisons/F1-contrasts.parquet')
    fig,ax=plt.subplots(figsize=(9,6)); positions=np.arange(len(contrast))
    ax.hlines(positions,contrast.family_lo,contrast.family_hi,color='steelblue',linewidth=2,label='Bonferroni 12-family CI')
    ax.scatter(contrast.point,positions,color='black',s=20); ax.axvline(0,color='gray',linestyle='--')
    ax.set(yticks=positions,yticklabels=contrast.protocol+' '+contrast.comparison,xlabel='Macro F1 difference')
    ax.invert_yaxis(); ax.legend(fontsize=8); fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(target/f'main-contrasts.{ext}',dpi=180)
    plt.close(fig)
    choices=pd.DataFrame(read(OUT/'selection/choices.json'))
    fig,axes=plt.subplots(1,4,figsize=(11,3),sharey=True)
    for ax,arm in zip(axes,ARMS[1:]):
        frequencies=choices[choices.arm.eq(arm)].t.value_counts().reindex(TS,fill_value=0)
        ax.bar(np.arange(4),frequencies); ax.set(xticks=np.arange(4),xticklabels=TS,title=arm,xlabel='Selected t')
    axes[0].set_ylabel('Outer deployment-fold roles'); fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(target/f'selection-frequency.{ext}',dpi=180)
    plt.close(fig)
    cls=pd.read_parquet(OUT/'scores/class-summary.parquet')
    fig,axes=plt.subplots(1,4,figsize=(14,4),sharey=True)
    short=['Bing','MDN','GitHub','Wikipedia','YT search','YT video']
    for ax,p in zip(axes,PROTOCOLS):
        for arm in ARMS:
            v=cls[cls.protocol.eq(p)&cls.arm.eq(arm)].set_index('label').loc[LABELS]
            ax.plot(np.arange(6),v.recall,marker='o',markersize=3,label=arm)
        ax.set(xticks=np.arange(6),xticklabels=short,title=p,ylim=(-.03,1.03)); ax.tick_params(axis='x',rotation=60)
    axes[0].set_ylabel('Recall'); axes[-1].legend(fontsize=7); fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(target/f'class-recall.{ext}',dpi=180)
    plt.close(fig)
    spectra=pd.read_parquet(OUT/'explanations/matrix-spectra.parquet')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for j,p in enumerate(PROTOCOLS):
        for ai,arm in enumerate(['KSR2','KSR3','KSR4']):
            df=spectra[spectra.protocol.eq(p)&spectra.arm.eq(arm)&spectra.coordinates.eq('raw')]
            axes[0].scatter(np.full(len(df),j+(ai-1)*.15),df.trace,s=15,label=arm if j==0 else None)
            axes[1].scatter(np.full(len(df),j+(ai-1)*.15),df.effective_rank,s=15)
    axes[0].set_yscale('log'); axes[0].set_ylabel('Native standardized trace (log scale)'); axes[0].legend()
    axes[1].set_ylabel('Effective rank')
    for ax in axes: ax.set_xticks(range(4),['SS','VLESS','Trojan','VMess'])
    fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(target/f'matrix-scale-spectrum.{ext}',dpi=180)
    plt.close(fig)
    write(target/'manifest.json',{'sha256':{p.name:sha(p) for p in target.glob('*') if p.suffix in ['.png','.pdf']},
                                 'plotted_all_protocols_and_arms':True})
    print('S16 five figures in PNG and PDF',flush=True)

def verify():
    c=start('verify'); baseline=read(OUT/'manifests/baseline-manifest.json')
    for p,h in baseline['sha256'].items(): require(sha(ROOT/p)==h,'Frozen baseline changed: '+p)
    for p,h in c['packages_sha256'].items(): require(sha(ROOT/p)==h,'Package changed: '+p)
    for p,h in c['outer_kernels_sha256'].items(): require(sha(ROOT/p)==h,'Kernel changed: '+p)
    require(sha(PLAN)==c['plan_sha256'],'Plan changed after registration')
    pred=checked_predictions(); choices={(x['outer'],x['protocol'],x['arm']):x['t'] for x in read(OUT/'selection/choices.json')}
    require(sha(OUT/'selection/choices.json')==read(OUT/'selection/complete.json')['choices_sha256'],'Choices changed')
    maxerror=0.; matrixerror=0.; fitcount=0
    for done in (OUT/'models').rglob('complete.json'):
        for name,h in read(done)['sha256'].items(): require(sha(done.parent/name)==h,'Model changed')
        fitcount+=len(read(done)['fits'])
    for done in (OUT/'kernels').rglob('complete.json'):
        for name,h in read(done)['sha256'].items(): require(sha(done.parent/name)==h,'Kernel changed')
    for done in (OUT/'regularizers').rglob('complete.json'):
        for name,h in read(done)['sha256'].items():
            a=artifact(done.parent/name,'verify')
            error=float((a['factor']@a['factor'].T-a['normalized_matrix']).abs().max()); matrixerror=max(matrixerror,error)
            require(error<1e-9,'Matrix factor replay failed')
    for r in outerroles(c):
        q=package(folder('packages',r['outer'],r['protocol'])/'query-post-hist.parquet','verify')
        require(set(q)=={'visit_id',*HIST},'Outer query forbidden columns')
        for arm in ARMS:
            t=0 if arm=='KSR0' else choices[(r['outer'],r['protocol'],arm)]
            model=artifact(folder('models',r['outer'],r['protocol'])/('zero.pt' if t==0 else f'{arm}-t{t:g}.pt'),'verify')
            new=probabilities(model,q)
            saved=pred[pred.outer.eq(r['outer'])&pred.protocol.eq(r['protocol'])&pred.arm.eq(arm)].set_index('visit_id').loc[new.visit_id]
            error=float(np.max(np.abs(new[[f'p{i}' for i in range(6)]].to_numpy()-saved[[f'p{i}' for i in range(6)]].to_numpy())))
            maxerror=max(maxerror,error); require(error<=1e-12,'Saved inference replay failed')
    for ledger in ['inner_matrix','inner_fit','inner_predict','select']:
        reads=read(OUT/'manifests'/f'{ledger}-ledger.json')['reads']
        require(all('/outer/' not in x['path'] and '/kernels/primary/' not in x['path'] for x in reads),'Inner stage accessed outer resource')
    for ledger in ['inner_predict','outer_predict']:
        reads=read(OUT/'manifests'/f'{ledger}-ledger.json')['reads']
        require(all(x['path'].endswith('query-post-hist.parquet') or '/models/' in x['path'] for x in reads),'Predict dependency violation')
    read_selection=read(OUT/'selection/complete.json')
    require(read_selection['sealed_unix']< (OUT/'predictions/complete.json').stat().st_mtime,'Outer inference precedes choices')
    innerlogs=pd.read_parquet(OUT/'manifests/inner-optimizer.parquet')
    require(len(innerlogs)==1040 and innerlogs.device.eq('cuda:0').all() and innerlogs['dtype'].eq('float64').all(),'Inner budget/device mismatch')
    require(pred.groupby('arm').size().eq(480).all() and pred.groupby(['arm','protocol','outer']).size().eq(24).all(),'Prediction coverage failed')
    result={'passed':True,'frozen_source_and_package_SHA_checked':True,'registered_entity_cross_fold':0,
      'registered_nested_entity_overlap':0,'inference_pre_labels_content_K_Gamma_reads':0,
      'inner_old_outer_kernel_reads':0,'probability_replay_max_error':maxerror,
      'matrix_factor_replay_max_error':matrixerror,'independent_models':fitcount,
      'zero_replay':read(OUT/'manifests/zero-replay.json')['passed'],'fit_and_matrix_and_inference_cuda_float64':True,
      'raw_PCAP_reads':0,'complete_TCP_epoch_proof':False,'online_single_side_qualification_proof':False}
    write(OUT/'verification.json',result); finish('verify',**result)
    print('S17 final verification passed',flush=True)

def table(frame):
    columns=list(frame.columns); lines=['| '+' | '.join(map(str,columns))+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{v:.6f}' if isinstance(v,(float,np.floating)) else str(v) for v in row)+' |')
    return '\n'.join(lines)

def report():
    require(read(OUT/'verification.json')['passed'],'Verification must pass before report')
    DOC.mkdir(parents=True,exist_ok=True)
    score=pd.read_parquet(OUT/'scores/protocol-summary.parquet'); contrasts=pd.read_parquet(OUT/'comparisons/F1-contrasts.parquet')
    choices=pd.DataFrame(read(OUT/'selection/choices.json')); freq=choices.groupby(['arm','t']).size().rename('roles').reset_index()
    cls=pd.read_parquet(OUT/'scores/class-summary.parquet'); flips=pd.read_parquet(OUT/'scores/error-flips.parquet')
    spectra=pd.read_parquet(OUT/'explanations/matrix-spectra.parquet')
    block=pd.read_parquet(OUT/'explanations/block-traces.parquet')
    energies=pd.read_parquet(OUT/'explanations/training-sensitivity.parquet')
    weights=pd.read_parquet(OUT/'explanations/weight-changes.parquet')
    innerlogs=pd.read_parquet(OUT/'manifests/inner-optimizer.parquet'); outerlogs=pd.read_parquet(OUT/'manifests/outer-optimizer.parquet')
    zero=read(OUT/'manifests/zero-replay.json'); verify_record=read(OUT/'verification.json')
    global_score=read(OUT/'scores/global-summary.json'); globalframe=pd.DataFrame([{k:v for k,v in x.items() if k!='pooled'} for x in global_score])
    positives=int(contrasts.family_positive.sum()); negatives=int(contrasts.family_negative.sum())
    zero_count=int(choices[choices.arm.eq('KSR2')].t.eq(0).sum())
    lead=f'本轮完成已登记的嵌套内容评价。真配核正则的12项主比较中，{positives}项校正区间完全大于0，{negatives}项完全小于0；其余区间包含0。KSR2在20个外层部署折角色中有{zero_count}个选择零权重。'
    conclusion='若某部署仅有点估计改善或区间包含零，不能升级为该部署已建立额外收益；也不能把不同臂选择不同t的结果全部归因于矩阵方向。'
    if positives==0:
        conclusion='本轮没有建立真配核结构优于公平L2、组级及post重复控制的校正正向证据。'+conclusion
    sections=[
      '# 概率核引导分类敏感度正则实验报告',
      '日期：2026年10月5日。原G系列冻结不变。\n\n'+lead+'\n\n'+conclusion,
      '## 研究问题与已冻结前序结果\n\n固定概率分类G4虽然优于入口原样和组级对照，却显著弱于充分post判别模型。本轮不再把核变成固定类别分布，而让核估计的条件波动几何约束自由训练的96维post LR。研究问题是这种结构能否优于有同样四候选选择预算的普通L2、匿名组核和单侧重复变化，而非必须超过旧G4。',
      '## 数据与任务范围\n\n四个已见部署SS、VLESS、Trojan、VMess，共23,566对合格排他TCP连接、480访问、30内容、六业务。每部署每内容四重复，每类五内容。部署连接数分别5,608、5,957、5,919、6,082。AnyTLS和Hy2不在本轮同粒度实验中。\n\n外层五个全局内容折，每折24训练内容96访问与6测试内容24访问。每个外层训练区再以其余四个原折轮流作为验证：18训练内容72访问、6验证内容24访问。跨部署的相同内容、全部重复、双侧及内部连接整体划分。登记实体未跨折；这不等于完整历史TCP epoch的普遍重建证明。\n\n标签顺序为：\n\n'+ '\n'.join(f'{i+1}. `{v}`' for i,v in enumerate(LABELS)),
      '## 表示与预处理\n\n每访问汇聚十个连接特征的固定箱频率，字节特征九箱、计数特征十箱，共96维。W/U上下行、P/E上下行、FR_packet_runs与R_unique_zero_runs保持前序定义，后两者没有互相替换。字节边界为1、256、1024、4096、16384、65536、262144、1048576；计数边界为1、2、3、4、8、16、32、64、128，right查箱，零独立且顶部开放。\n\n标准化均值和总体标准差只拟合允许训练post访问，常数维尺度设1，不删除维度。分类器六类权重96×6和六偏置，共582参数。没有IP、端口、SNI、URL、业务真值、内容ID或协议身份数值编码；模型按已知部署路由独立拟合，不是统一未知协议模型。',
      r'## 核矩阵与损失'+'\n\n'+r'连接质量为 $1/(r_u n_v)$，内容等权、内容内访问等权、访问内连接等权。入口频率nu不平滑，M1与M2均保持alpha=beta=1。M2只读独立打乱的匿名单侧包，保留内容及质量，移除pair/session/carrier/logical身份。'+'\n\n'+r'$\Gamma_j=\mathrm{diag}(\nu_j^T K_j)-K_j^T\mathrm{diag}(\nu_j)K_j$，边际来自同一nu和K。八个W/U/P/E块权重1/12，两个交互块1/6。按 $D^{-1}\Gamma_hD^{-1}$ 转换，再整体trace归一到96，不逐块归一。post重复控制同样十块，按训练内容四访问残差总体方差计算，分母4，不引入跨特征协方差。'+'\n\n'+r'额外项为 $\lambda\|P_6\Theta L\|_F^2/5$。t仅为0、0.25、1、4，lambda为0、0.000625、0.0025、0.01。基本loss为平均CE加0.0005倍权重平方和，偏置不惩罚。普通L2 rho为0.001、0.00125、0.002、0.005。零候选直接执行原目标分支。'+'\n\n'+r'CUDA上的PSD因子按 $q=\sqrt k$、$L_a=\mathrm{diag}(q)(I-qq^T)$ 构造。QR仅把因子压缩到96列，保存压缩前因子与误差；没有用特征值截断掩盖非PSD。经验未平滑核只作描述，没有另设分类臂。'+
       '\n\nGamma是分类敏感度先验，不是已验证的访问级噪声协方差或合法TCP生成器；二次项也不等于期望CE。共同trace归一丢弃总体波动强度，平滑可产生并放大小幅波动。严格正核理论rank86不等于观测了86种代理噪声。',
      '## 方法与资源公平性\n\n'+table(pd.DataFrame([
         ['KSR0','原固定G1复现','无选择','完整训练post及标签'],
         ['KSR1','普通L2','四候选独立内层选择','相同post及标签'],
         ['KSR2','真配核结构正则','相同四候选','另有训练pre及精确对应'],
         ['KSR3','匿名内容组核结构正则','相同四候选','另有同内容两侧及质量，无实例身份'],
         ['KSR4','post重复块正则','相同四候选','训练内容分组，四post重复']
      ],columns=['臂','方法','选择规则','训练资源'])),
      '## 嵌套选择与优化配置\n\n每个方法以四内层合并96访问的完整六类macro F1选t，差距不超过1e-12时选最小t。CE/Brier不参与选择。每内层重新估计nu、核、尺度和重复矩阵，不复用见过验证内容的旧外层核；封存80条选择后才拟合选定外层方法。没有生成外层四候选性能曲线。\n\n所有拟合、矩阵计算和推理均为Pytorch312 CUDA float64、关闭TF32、确定性算法。LR从零初始化，LBFGS max_iter=500、tolerance_grad=1e-9、tolerance_change=1e-12、strong_wolfe。停止可以由目标变化触发，不要求最终梯度全部小于1e-9。\n\n'+table(pd.DataFrame([
          ['内层',len(innerlogs),float(innerlogs.seconds.sum()),int(innerlogs.hit_iteration_budget.sum()),float(innerlogs.max_gradient.max())],
          ['外层含零参照',len(outerlogs),float(outerlogs.seconds.sum()),int(outerlogs.hit_iteration_budget.sum()),float(outerlogs.max_gradient.max())]
      ],columns=['阶段','独立拟合数','拟合计时合计秒','触及500迭代数','最大最终梯度'])),
      '## 零权重复现与工程资格\n\n20个原G1零重放均通过预登记容差：目标1e-12、梯度1e-10、概率1e-8且类别完全一致。实际最大概率误差为'+str(max(r['probability_error'] for r in zero['roles']))+'。人工矩阵测试和最终SHA、依赖、模型重载验证均通过。\n\n最终推理仅加载冻结582参数模型、训练尺度和post查询，不加载pre、Gamma或K。标签在候选/最终预测封存之后由独立评分或选择进程读取。记录读取白名单不是OS级安全沙箱；共同资格和父访问范围仍来自双侧离线关联。',
      '## 外层总体结果\n\n'+table(score.sort_values(['protocol','arm']))+'\n\n'+table(globalframe)+'\n\n![四部署五臂F1](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/protocol-F1.png)',
      '## 预登记十二项主比较\n\n10000次六业务分层内容bootstrap，每类五内容重采样，四重复及全部部署随内容抽取，共用索引。普通95%区间与12项Bonferroni家族对应的99.583333%边际区间都报告。区间条件于已选择固定模型，未重做嵌套拟合，不是外部验证或研究者盲测。区间跨零不是等效证明。\n\n'+table(contrasts)+'\n\n![主比较校正区间](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/main-contrasts.png)',
      '## 全部内层强度选择\n\n'+table(freq)+'\n\n'+table(choices.sort_values(['protocol','outer','arm']))+'\n\n![所选强度](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/selection-frequency.png)',
      '## 逐业务结果和错误变化\n\n'+table(cls.sort_values(['protocol','label','arm']))+'\n\n'+table(flips)+'\n\n![逐业务recall](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/class-recall.png)\n\n完整内容错误、访问级修复与新增错误及六类混淆矩阵保存在scores目录，不以困难YouTube业务退化为由删类或重选队列。',
      '## 训练矩阵尺度和谱\n\n下表按外层角色报告原生标准化与整体trace归一后的谱。原生尺度不是归一后的惩罚强度，各族实际trace也不会因登记权重而自动一致。\n\n'+table(spectra.drop(columns=['symmetry_error','PSD_tolerance']).sort_values(['protocol','outer','arm','coordinates']))+'\n\n![矩阵尺度及有效rank](../../outputs/kernel-sensitivity-regularization-20261005/run-01/figures/matrix-scale-spectrum.png)',
      '## 特征块尺度与训练敏感度\n\n以下为外层五折平均，仅作训练描述，不参与重新选矩阵或lambda。\n\n'+table(block.groupby(['protocol','arm','feature'])[['hist_trace','standardized_trace']].mean().reset_index())+'\n\n'+table(energies.groupby(['protocol','classifier_arm','matrix_arm','family']).sensitivity.sum().div(5).reset_index())+'\n\n'+table(weights.groupby(['protocol','arm'])[['weight_Frobenius','baseline_weight_difference','common_class_weight_max']].mean().reset_index()),
      '## 完整内容错误台账\n\n'+table(pd.read_parquet(OUT/'scores/content-errors.parquet').sort_values(['protocol','content_id','arm'])),
      '## 结论与停止记录\n\n'+lead+'\n\n'+conclusion+'\n\n本轮到此冻结，不增加权重、温度、特征、核条件或网络。不将负结果解释为漂移概率信息永远无用；也不将局部正向点估计扩展为未知部署、跨日期、真实DIRECT或无索引在线识别。推理路由已知且数据资格离线给定，所有部署历史上已被反复研究，因此回顾性选择风险仍在。',
      '## 产物与复现\n\n代码在`eval/kernel_sensitivity_regularization`。本次输出目录为`outputs/kernel-sensitivity-regularization-20261005/run-01`。依次运行setup的inventory/prepare/tests/zero/register，train的inner-matrix/inner-fit/inner-predict/select/outer-matrix/outer-fit/predict，results的evaluate/bootstrap/explain/plot/verify/report。封存后不得重新打包或改变源文件；拟合阶段支持complete.json断点续跑。详细命令见代码README。\n\n预测2400行、选择80条、内层800个核bundle、外层200个核副本并核验原文件、全部谱与因子保存；SHA契约、实际读取台账、优化记录和验证报告均独立存储。本文档依据这些冻结产物生成，未扫描PCAP。'
    ]
    (DOC/'formal-report.md').write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    (DOC/'result-interpretation.md').write_text('# 核敏感度正则结果解读\n\n'+lead+'\n\n'+conclusion+'\n\n'+table(score.pivot(index='protocol',columns='arm',values='F1').reset_index())+'\n\n'+table(contrasts)+'\n\n本轮已经停止，不依照外层结果扩大权重范围。完整逐业务、选择和矩阵描述见formal-report.md。\n',encoding='utf-8')
    (DOC/'model-card.md').write_text('# 核敏感度正则模型卡\n\n用途为四个已见TCP代理部署、给定父访问及合格连接集合后的六业务识别。每部署五个外层模型，每个582参数，输入96维post箱频率与部署路由。尺度来自训练post；训练真配和组级核不在推理时读取。内容全局分折，全部重复、双侧和内部连接随父内容划分。\n\n不支持已验证的未知部署、真实DIRECT、跨日期、任意配置或在线无索引切分。AnyTLS和Hy2不在本轮。矩阵为条件波动几何先验，不是协议精确开销、纯噪声或合法TCP扰动。统计区间条件于固定选择模型，未外部验证。\n',encoding='utf-8')
    (DOC/'implementation-status.md').write_text('# 核敏感度正则实施状态\n\nS00至S18已完成，最终验证通过；预登记十二项主比较全部保留。\n\n'+lead+'\n\n旧G/Q产物SHA不变。本轮冻结，不自动新增诊断或训练。CUDA矩阵因子最大重放误差：'+str(verify_record['matrix_factor_replay_max_error'])+'。\n',encoding='utf-8')
    (DOC/'experiment-contract.md').write_text('# 核敏感度正则实验契约\n\n预登记原子方案位于plan/kernel-conditioned-sensitivity-regularization-plan-20261005.md。机器契约在outputs/kernel-sensitivity-regularization-20261005/run-01/manifests/experiment-contract.json，封存新科学代码、所有角色包、外层核SHA、四候选、优化器和12项检验家族。\n\n内层18内容重新估核和尺度，外层24内容仅在选择封存后拟合。所有方法有同样完整post监督、同样四候选；矩阵臂额外资源及解释边界详见formal-report。t=0直接复现原G1，20个工程重放全部通过。\n',encoding='utf-8')
    write(OUT/'manifests/delivery-manifest.json',{'documents_sha256':{rel(p):sha(p) for p in DOC.glob('*.md')},
          'README_sha256':sha(Path(__file__).parent/'README.md'),'stopped':True,'main_family':12})
    write(OUT/'progress.json',{'stage':'S18 complete and frozen','time_unix':time.time(),'family_positive':positives,
          'family_negative':negatives,'KSR2_zero_roles':zero_count,'requires_new_authorization_for_next_experiment':True})
    print('S18 report complete; candidate frozen',flush=True)

if __name__=='__main__':
    {'evaluate':evaluate,'bootstrap':uncertainty,'explain':explain,'plot':plot,'verify':verify,'report':report}[sys.argv[1]]()
