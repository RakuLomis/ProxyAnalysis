"""Fixed linear privileged-information controls with post-only prediction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..paired_information.prepare import digest, table
from ..paired_information.reference_retrain import SCALAR_NAMES
from ..reproducibility.preflight import write_json, write_table
from .business_features import load_config, verify
from .business_splits import outer_assignment, teacher_assignment, disjoint, donors


def matrix(rows, side):
    return np.asarray([[r[side].get(k) for k in SCALAR_NAMES] for r in rows],dtype=float)


class LinearStudent:
    def __init__(self,cfg): self.cfg=cfg

    def fit(self,x,targets):
        targets=np.asarray(targets,dtype=float)
        if targets.ndim!=2 or len(x)!=len(targets) or not np.all(np.isfinite(targets)):
            raise ValueError('Invalid target shape or values')
        if np.any(targets<0) or not np.allclose(targets.sum(axis=1),1):
            raise ValueError('Targets must be probability vectors')
        self.preprocess=make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler())
        z=self.preprocess.fit_transform(x)
        k=targets.shape[1]
        expanded=np.repeat(z,k,axis=0); labels=np.tile(np.arange(k),len(z)); weight=targets.ravel()
        active=weight>0
        self.model=LogisticRegression(C=self.cfg['model_C'],max_iter=self.cfg['max_iter'],random_state=self.cfg['seed'])
        with warnings.catch_warnings():
            warnings.simplefilter('error',ConvergenceWarning)
            self.model.fit(expanded[active],labels[active],sample_weight=weight[active])
        if list(self.model.classes_)!=list(range(k)): raise ValueError('Missing training class')
        return self

    def predict(self,post_matrix):
        return self.model.predict_proba(self.preprocess.transform(post_matrix))

    def state(self):
        return {'coef':self.model.coef_.tolist(),'intercept':self.model.intercept_.tolist(),
                'imputer_statistics':self.preprocess[0].statistics_.tolist(),
                'scaler_mean':self.preprocess[1].mean_.tolist(),'scaler_scale':self.preprocess[1].scale_.tolist(),
                'iterations':self.model.n_iter_.tolist()}


def scores(y,p):
    y=np.asarray(y); p=np.clip(np.asarray(p),1e-12,1)
    return {'n':len(y),'log_loss_bits':float(np.mean(-np.log2(p[np.arange(len(y)),y]))),
        'macro_f1':float(f1_score(y,np.argmax(p,axis=1),average='macro')),
        'balanced_accuracy':float(balanced_accuracy_score(y,np.argmax(p,axis=1))),
        'brier_multiclass':float(np.mean(np.sum((p-np.eye(p.shape[1])[y])**2,axis=1))),
        'confusion_matrix':confusion_matrix(y,np.argmax(p,axis=1),labels=np.arange(p.shape[1])).tolist()}


def run(cfg,smoke=False):
    verify(cfg); root=Path(cfg['output_root'])
    gate=json.loads((root/'identity-gate.json').read_text(encoding='utf-8'))
    if not gate['passed']: raise ValueError('Identity/cohort gate not passed')
    for name,expected in gate['source_hashes'].items():
        if digest(root/name)!=expected: raise ValueError('Audited feature source changed')
    rows=[r for r in table(root/'side-summaries.parquet') if r['selection']=='observed' and r['primary_candidate']]
    if len(rows)!=240: raise ValueError('Frozen 240-member cohort required')
    assignment=outer_assignment(rows,cfg['seed'])
    out=root/('smoke' if smoke else 'learning'); out.mkdir(exist_ok=False)
    write_json(out/'run-contract.json',{'config':cfg,'source_sha256':digest(root/'side-summaries.parquet'),
        'identity_gate_sha256':digest(root/'identity-gate.json'),
        'code_hashes':{str(p):digest(p) for p in Path(__file__).parent.glob('*.py')},
        'smoke_not_research_result':smoke,'feature_allowlist':list(SCALAR_NAMES)})
    write_json(out/'outer-splits.json',assignment)
    predictions=[]; teachers=[]; mappings=[]; fits=[]; splits=[]
    def fitted(x,q,info):
        model=LinearStudent(cfg).fit(x,q)
        fits.append({**info,'state':model.state()})
        return model
    def record(rows,probabilities,task,protocol,fold,scheme,arm,seed=-1):
        for row,p in zip(rows,probabilities):
            predictions.append({'session_id':row['session_id'],'content_id':row['content_id'],
                'label_id':row['label_id'],'truth':labels.index(row['label_id']),
                'task':task,'protocol':protocol,'outer_fold':fold,'teacher_scheme':scheme,
                'arm':arm,'mismatch_seed':seed,'probabilities':p.tolist(),
                'loss_bits':float(-np.log2(max(p[labels.index(row['label_id'])],1e-12)))})
    for task in ('six_business','youtube_activity'):
        for protocol in cfg['protocols']:
            selected=[r for r in rows if r['protocol']==protocol and (task=='six_business' or r['label_id'].startswith('youtube.com::'))]
            labels=sorted({r['label_id'] for r in selected}); k=len(labels)
            for fold in range(1 if smoke else 5):
                train=[r for r in selected if assignment[r['content_id']]!=fold]
                test=[r for r in selected if assignment[r['content_id']]==fold]
                disjoint(train,test)
                y=np.asarray([labels.index(r['label_id']) for r in train]); hard=np.eye(k)[y]
                xt=matrix(test,'post'); x=matrix(train,'post')
                context={'task':task,'protocol':protocol,'outer_fold':fold}
                base=fitted(x,hard,{**context,'arm':'M0','scheme':-1})
                record(test,base.predict(xt),task,protocol,fold,-1,'M0')
                # Separate teacher diagnostics; never used for student tuning or selection.
                teacher=fitted(matrix(train,'pre'),hard,{**context,'arm':'pre_teacher_full','scheme':-1})
                record(test,teacher.predict(matrix(test,'pre')),task,protocol,fold,-1,'pre_teacher_diagnostic')
                for scheme in (cfg['teacher_schemes'][:1] if smoke else cfg['teacher_schemes']):
                    partition=teacher_assignment(train,scheme)
                    q={side:np.zeros((len(train),k)) for side in ('pre','post')}
                    for held in (0,1):
                        tr=[i for i,r in enumerate(train) if partition[r['content_id']]!=held]
                        va=[i for i,r in enumerate(train) if partition[r['content_id']]==held]
                        a,b=[train[i] for i in tr],[train[i] for i in va]
                        disjoint(a,b,test)
                        splits.append({**context,'scheme':scheme,'teacher_holdout':held,
                            'train_ids':[r['session_id'] for r in a],'holdout_ids':[r['session_id'] for r in b],
                            'test_ids':[r['session_id'] for r in test]})
                        for side in ('pre','post'):
                            model=fitted(matrix(a,side),hard[tr],{**context,'arm':side+'_teacher_oof','scheme':scheme,'held':held})
                            q[side][va]=model.predict(matrix(b,side))
                    for i,r in enumerate(train):
                        teachers.append({**context,'scheme':scheme,'session_id':r['session_id'],
                            'teacher_holdout':partition[r['content_id']], 'pre_probabilities':q['pre'][i].tolist(),
                            'post_probabilities':q['post'][i].tolist()})
                    cross=donors(train,partition)
                    arms=[('M1',q['post'],None,-1),('M2',q['pre'],np.arange(len(train)),-1),('M3',q['pre'][cross],cross,-1)]
                    if not smoke:
                        for seed in cfg['within_content_seeds']:
                            perm=donors(train,partition,'within_content',seed)
                            arms.append(('M3_within_content',q['pre'][perm],perm,seed))
                    for arm,prob,perm,seed in arms:
                        target=(1-cfg['alpha'])*hard+cfg['alpha']*prob
                        model=fitted(x,target,{**context,'arm':arm,'scheme':scheme,'mismatch_seed':seed})
                        record(test,model.predict(xt),task,protocol,fold,scheme,arm,seed)
                        if perm is not None:
                            mappings.extend({**context,'scheme':scheme,'arm':arm,'seed':seed,
                                'receiver':r['session_id'],'donor':train[perm[i]]['session_id'],
                                'teacher_holdout':partition[r['content_id']]} for i,r in enumerate(train))
                print(json.dumps({**context,'completed_fold':True,'fresh_fit_count':len(fits)}),flush=True)
                write_table(out/'oof.parquet',predictions)
                write_table(out/'teacher-oof.parquet',teachers)
                write_table(out/'pair-maps.parquet',mappings)
                write_json(out/'fit-ledger.json',fits)
                write_json(out/'teacher-splits.json',splits)
            if smoke: break
        if smoke: break
    write_json(out/'complete.json',{'fresh_fits':len(fits),'prediction_rows':len(predictions),
        'artifacts':{name:digest(out/name) for name in ['oof.parquet','teacher-oof.parquet','pair-maps.parquet','fit-ledger.json','teacher-splits.json']}})


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args(); run(load_config(),args.smoke)


if __name__=='__main__': main()
