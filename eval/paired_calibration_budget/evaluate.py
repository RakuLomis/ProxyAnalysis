"""Independent post-only CUDA inference; labels are loaded only after prediction seal."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.calibration_budget.common import *
from proxy_analysis.conditional_drift.model import device,torch

def infer():
    assert read(OUT/'training-progress.json')=={'completed':2160,'total':2160,'status':'complete'}
    for p,h in read(OUT/'training-contract.json')['files'].items():assert sha(p)==h
    rows=[];audits=[];dev=device();largest=0.;inputs={}
    for folder in sorted((OUT/'classifiers').iterdir()):
        complete=read(folder/'complete.json');assert complete['cuda'] and not complete['H_read'] and not complete['U_post_read']
        for p,h in complete['files'].items():assert sha(p)==h
        meta=read(OUT/'bundles'/folder.name/'manifest.json')
        hp=OUT/'evaluation'/folder.name/'H_post.parquet';inputs[str(hp)]=sha(hp)
        frame=pd.read_parquet(hp);assert 'label_id' not in frame and len(frame)==24
        assert not set(frame.session_id)&(set(meta['C_sessions'])|set(meta['U_sessions']))
        assert not set(frame.content_id)&(set(meta['C_contents'])|set(meta['U_contents']))
        raw=frame[NUMERIC].to_numpy(float);jobs=[]
        for path in sorted(folder.glob('*.pt')):
            state=torch.load(path,map_location=dev,weights_only=False);job=state['job'];jobs.append(job)
            assert state['contract']==sha(OUT/'training-contract.json') and state['C_hash']==meta['C_hash']
            assert set(state['scaler_fit_sessions'])==set(meta['C_sessions'])
            model=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(dev)
            model.load_state_dict(state['head']);model.eval()
            x=torch.tensor((np.log1p(raw)-state['mean'])/state['scale'],device=dev,dtype=torch.float32)
            with torch.no_grad():
                p=torch.softmax(model(x),-1)
                # Reload a second model and change inference batch boundaries.
                replay=torch.nn.Sequential(torch.nn.Linear(7,32),torch.nn.ReLU(),torch.nn.Linear(32,6)).to(dev)
                replay.load_state_dict(torch.load(path,map_location=dev,weights_only=False)['head']);replay.eval()
                q=torch.cat([torch.softmax(replay(b),-1) for b in x.split(6)])
                torch.testing.assert_close(p,q,atol=2e-6,rtol=2e-5)
                assert torch.equal(p.argmax(1),q.argmax(1));largest=max(largest,float((p-q).abs().max()))
            probs=p.cpu().numpy()
            for i,r in enumerate(frame[IDENTITY].to_dict('records')):
                rows.append({**r,**job,'classes_json':json.dumps(state['classes']),**{f'p{j}':float(probs[i,j]) for j in range(6)}})
        jobs=pd.DataFrame(jobs)
        for seed,g in jobs.groupby('seed'):
            assert len(g)==6 and g.initial_hash.nunique()==1 and g[g.arm!='B0'].schedule_hash.nunique()==1
        audits.append({'scenario':folder.name,'models':18,'CUDA':True,'reload_passed':True,'C_only_scaler':True,'heldout_disjoint':True})
    predictions=save('predictions',rows);assert len(predictions)==51840
    assert not predictions.duplicated(['protocol','k','rotation','seed','arm','session_id']).any()
    save('classifier-audit',audits)
    write(OUT/'prediction-seal.json',{'passed':True,'rows':len(predictions),'models':2160,'CUDA':True,'max_replay_probability_difference':largest,
        'labels_read':False,'H_pre_read':False,'U_post_read':False,'predictions_hash':sha(OUT/'predictions.parquet'),'post_inputs':inputs,'script_hash':sha(__file__)})
    print('Sealed predictions',len(predictions),flush=True)

def label():
    seal=read(OUT/'prediction-seal.json');assert seal['passed'] and sha(OUT/'predictions.parquet')==seal['predictions_hash']
    p=pd.read_parquet(OUT/'predictions.parquet');labels=[]
    for folder in sorted((OUT/'evaluation').iterdir()):
        f=pd.read_parquet(folder/'H_labels.parquet');f['scenario']=folder.name;labels.append(f)
    labels=pd.concat(labels);assert not labels.duplicated(['scenario','session_id']).any()
    result=p.merge(labels,on=['scenario','session_id','content_id'],validate='many_to_one')
    assert len(result)==51840 and result.label_id.notna().all()
    classes=json.loads(result.classes_json.iloc[0]);assert result.classes_json.nunique()==1
    result['target']=result.label_id.map({s:i for i,s in enumerate(classes)});assert result.target.notna().all()
    result['prediction']=result[[f'p{i}' for i in range(6)]].to_numpy().argmax(1)
    save('scored-predictions',result)
    write(OUT/'scoring-seal.json',{'prediction_seal':sha(OUT/'prediction-seal.json'),'classes':classes,'rows':len(result),'scored_hash':sha(OUT/'scored-predictions.parquet')})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['infer','label'],required=True);a=ap.parse_args()
    infer() if a.stage=='infer' else label()
