"""Regression: reproduce original error, safe nested schema and cache readback."""
from common import *
from payload import normalize,assert_identical,numpy_paths
import pickle
import subprocess


def run():
    with stage('payload_tests'):
        out=OUT/'audits/payload-fixtures'
        bad=writable(out/'original-numpy-scalar.pt')
        original=dict(checks=dict(implicit_f=dict(precision_risk=np.bool_(False))))
        torch.save(original,bad)
        rejected=False;message=None
        try:torch.load(bad,map_location=device(),weights_only=True)
        except pickle.UnpicklingError as e:rejected=True;message=str(e)
        require(rejected and 'numpy' in message,'Original serialization error not reproduced')
        q=torch.ones(10,device=device(),dtype=torch.float64)
        theta=torch.arange(582,device=device(),dtype=torch.float64).reshape(6,97)/1000
        sample=dict(q=q,theta_f=theta,theta_v=theta+1e-15,Q_f=np.float64(.25),Q_v=.25,
                    gradient_f=q*.001,gradient_v=q*.001,
                    checks=dict(implicit_f=dict(precision_risk=np.bool_(False),passed=True),
                                implicit_v=dict(precision_risk=np.bool_(True),condition=np.float64(123.5))),
                    counter=np.int64(2**54+1),signed_zero=np.float64(-0.),name=np.str_('sample'),
                    history=[np.int32(3),(np.float64(.05),np.bool_(True))],
                    optimizer_state=dict(state={0:dict(step=torch.tensor(20.),exp_avg=q*.1,exp_avg_sq=q*.01)},
                                         param_groups=[dict(lr=.05,betas=(.9,.999),eps=1e-8,params=[0])]))
        safe=normalize(sample);require(not numpy_paths(safe),'NumPy metadata survived normalization')
        require(safe['counter']==2**54+1 and safe['signed_zero'].hex()=='-0x0.0p+0','Normalization lost exact scalar values')
        path=out/'safe-feedback-cache.pt'
        put(sample,path,kind='synthetic',source_data_used=False)
        # The SAME loader used on a formal P/T-P cache hit.
        hit=own(path);assert_identical(safe,hit)
        require(type(hit['checks']['implicit_f']['precision_risk']) is bool,'Safe scalar type not bool')
        model=writable(out/'real-cache-layout.pt')
        put(dict(q=q,gradient_f=q,Q_f=.4,checks=sample['checks']),model,source_data_used=False)
        a=own(model);b=own(model);assert_identical(a,b)
        negative=0
        for value in [object(),Path('not-a-checkpoint'),np.array([1,2,3])]:
            try:normalize(dict(unsupported=value))
            except TypeError:negative+=1
            else:raise RuntimeError('Unsupported object admitted')
        for value in [dict(safe,counter=safe['counter']+1),dict(safe,signed_zero=0.),dict(safe,q=q+1e-15)]:
            try:assert_identical(safe,value)
            except RuntimeError:negative+=1
            else:raise RuntimeError('Readback mismatch admitted')
        # A fresh interpreter has no accidental process-level serialization allowlist.
        command=[sys.executable,str(Path(__file__).resolve()),'readback',str(path),sha(path)]
        env=dict(os.environ);env['PYTHONIOENCODING']='utf-8'
        result=subprocess.run(command,check=True,capture_output=True,text=True,encoding='utf-8',env=env,timeout=45)
        report=dict(passed=True,old_error_reproduced=True,original_numpy_paths=numpy_paths(sample),
                    safe_numpy_paths=numpy_paths(safe),safe_loader='weights_only=True',unsafe_loads=0,globals_allowlisted=0,
                    fresh_process_passed=True,fresh_process_stdout=result.stdout.strip(),negative_tests=negative,
                    tensor_byte_replay=True,signed_zero_preserved=True,large_integer_preserved=True,
                    actual_H_U_reads=0,actual_source_LR_fits=0,checks_before_publish=True)
        write(OUT/'audits/payload-roundtrip.json',report)
        progress('payload_roundtrip_verified',negatives=negative,fresh_process=True)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='readback':
        configure();p=Path(sys.argv[2]);require(sha(p)==sys.argv[3],'Fresh process fixture hash')
        require(not torch.serialization.get_safe_globals(),'Unexpected process serialization allowlist')
        v=torch.load(p,map_location=device(),weights_only=True)
        require(not numpy_paths(v) and type(v['checks']['implicit_f']['precision_risk']) is bool,'Fresh process unsafe schema')
        require(v['q'].is_cuda and v['q'].dtype==torch.float64,'Fresh process CUDA schema')
        print('fresh-process safe readback verified',flush=True)
    else:run()
