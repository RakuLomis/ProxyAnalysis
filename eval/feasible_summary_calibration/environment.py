"""Record the actual runtime without reading experimental samples."""
import sys,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from proxy_analysis.feasible_summary_calibration.common import *
from proxy_analysis.conditional_drift.model import device,torch
def main():
    device();prop=torch.cuda.get_device_properties(0)
    write(OUT/'environment.json',{'python_executable':sys.executable,'python':sys.version,'platform':platform.platform(),'torch':str(torch.__version__),
        'cuda_runtime':torch.version.cuda,'cudnn':torch.backends.cudnn.version(),'gpu':prop.name,'gpu_memory_bytes':prop.total_memory,
        'numpy':np.__version__,'pandas':pd.__version__,'torch_num_threads':torch.get_num_threads(),'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),
        'TF32_matmul':torch.backends.cuda.matmul.allow_tf32,'TF32_cudnn':torch.backends.cudnn.allow_tf32,'training_dtype':'float32','ridge_and_decoder_dtype':'float64'})
    print(read(OUT/'environment.json'),flush=True)
if __name__=='__main__':main()
