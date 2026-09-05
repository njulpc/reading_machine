"""NF4 weight reference; --native runs real double-quantized QLoRA when dependencies exist."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from numerics import *
def native():
 from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
 from peft import LoraConfig,get_peft_model,prepare_model_for_kbit_training
 checkpoint=resolve_model()
 cfg=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
 model=AutoModelForCausalLM.from_pretrained(checkpoint,local_files_only=True,quantization_config=cfg,device_map='auto')
 model=get_peft_model(prepare_model_for_kbit_training(model),LoraConfig(r=16,lora_alpha=32,target_modules=['q_proj','k_proj','v_proj','o_proj'],task_type='CAUSAL_LM'))
 tok=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True);model.train();opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4,weight_decay=0)
 losses=[]
 # Local language smoke training: not the paper's private ASR corpus or 5-epoch protocol.
 for text in CAL:
  batch=tok(text,return_tensors='pt').to(model.device);out=model(**batch,labels=batch.input_ids);opt.zero_grad();out.loss.backward();opt.step();losses.append(float(out.loss))
 return {'native_QLoRA':True,'train_losses':losses,'rank':16,'alpha':32,'training':'four local texts; lr=1e-4 demo override because paper HTML omits coefficient'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--native',action='store_true');p.add_argument('--output-json');a=p.parse_args()
 if a.native:r=native()
 else:
  r=run_full('nf4-double');r.update({'native_QLoRA':False,'NF4_block':64,'scale_block':256,'cpu_nested_scale_quantization_tested':True,'double_quantization_backend':'groupwise signed INT8 CPU proxy; not bitsandbytes','boundary':'peft and bitsandbytes are absent; --native is provided but not executed. A CPU engineering proxy applies block-64 NF4 and groupwise INT8 scale quantization to all real Qwen3-0.6B backbone Linear weights, then runs forward/generation; it is not the native bitsandbytes nested format and does not train adapters. Private ASR checkpoint/audio unavailable; no CER or adapter-memory claim.'})
 r['full_paper_reproduced']=False;save(r,a.output_json)
if __name__=='__main__':main()
