"""Minima numerical W4A4 transfer. Qwen3-0.6B has no Gated DeltaNet."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def harmonize(global_scales,local_scales):
 shared=max(global_scales)
 return shared,[(s*g/shared).clamp(max=448).to(torch.float8_e4m3fn).float() for g,s in zip(global_scales,local_scales)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-json');a=p.parse_args()
 x=torch.tensor([0,.25,.75,1.25,1.75,2.5,3.5,5.]);torch.testing.assert_close(e2m1(x),torch.tensor([0,0,1,1,2,2,4,4.]))
 g,s=harmonize([1.,2.],[torch.tensor([2.]),torch.tensor([1.])]);assert g==2 and s[0]==s[1]
 r=run_full('nvfp4');r.update({'weight_block':16,'activation_block':16,'scale_format':'E4M3 plus FP32 global','harmonization_test':'PASS','boundary':'No GDN in Qwen3-0.6B; no 27B/32K experiments or native FP4 GEMM. Static globals calibrated on four local texts, not paper 128x32K. FP8 KV calibration not integrated.'});save(r,a.output_json)
if __name__=='__main__':main()
