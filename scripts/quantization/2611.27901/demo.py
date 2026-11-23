"""QuantStream3D KV quantizer transplant to Qwen3; not geometry QAD reproduction."""
import argparse, json, math, types
import torch


def rotate(x):
    """Block-diagonal H64/8, after RoPE; Qwen head dimension can exceed 64."""
    shape = x.shape
    assert shape[-1] % 64 == 0
    y = x.float().reshape(*shape[:-1], -1, 64)
    for width in (1, 2, 4, 8, 16, 32):
        z = y.reshape(*y.shape[:-1], -1, 2, width)
        a, b = z[..., 0, :], z[..., 1, :]
        y = torch.stack((a+b, a-b), -2).reshape_as(y)
    return (y / 8).reshape(shape).to(x.dtype)


class Packed:
    def __init__(self, x, bits):
        self.shape, self.dtype, self.bits = x.shape, x.dtype, bits
        n = x.shape[-2]
        pad = (-n) % 64
        y = torch.cat((x, x[..., -1:, :].expand(*x.shape[:-2], pad, x.shape[-1])), -2) if pad else x
        y = y.float().reshape(*x.shape[:-2], -1, 64, x.shape[-1])
        lo, hi = y.amin(-2, keepdim=True), y.amax(-2, keepdim=True)
        self.scale = torch.where(hi > lo, (hi-lo)/(2**bits-1), torch.ones_like(lo))
        self.zero = torch.where(hi > lo, (-lo/self.scale).round(), -lo)
        q = (torch.round(y/self.scale)+self.zero).clamp(0, 2**bits-1).to(torch.uint8).flatten()
        self.group_shape = y.shape
        self.count = q.numel()
        per_byte = 8//bits
        q = torch.nn.functional.pad(q, (0, (-len(q)) % per_byte)).reshape(-1, per_byte)
        self.codes = torch.zeros(q.shape[0], dtype=torch.uint8, device=x.device)
        for j in range(per_byte): self.codes |= q[:, j] << (bits*j)

    def decode(self):
        q = torch.stack([(self.codes >> (self.bits*j)) & (2**self.bits-1) for j in range(8//self.bits)], -1)
        q = q.flatten()[:self.count].reshape(self.group_shape).float()
        y = self.scale * (q-self.zero)
        return y.reshape(*self.shape[:-2], -1, self.shape[-1])[..., :self.shape[-2], :].to(self.dtype)

    def nbytes(self):
        return sum(t.numel()*t.element_size() for t in (self.codes,self.scale,self.zero))


def self_test():
    torch.manual_seed(7)
    q,k = torch.randn(2,3,7,128),torch.randn(2,3,11,128)
    err = ((q@k.transpose(-1,-2))-(rotate(q)@rotate(k).transpose(-1,-2))).abs().max().item()
    assert err < 2e-5, err
    for n in (1, 63, 64, 65, 128):
        for bits in (2,4):
            x=torch.randn(1,2,n,128)
            p=Packed(x,bits); y=p.decode()
            assert y.shape==x.shape and torch.isfinite(y).all()
            # Independent scalar reference with the same per-channel grouping.
            for start in range(0,n,64):
                z=x[...,start:start+64,:];lo=z.amin(-2,keepdim=True);hi=z.amax(-2,keepdim=True)
                s=torch.where(hi>lo,(hi-lo)/(2**bits-1),torch.ones_like(lo))
                zero=torch.where(hi>lo,(-lo/s).round(),-lo)
                ref=s*((z/s).round().add(zero).clamp(0,2**bits-1)-zero)
                ref=torch.where(hi>lo,ref,lo)
                assert torch.allclose(y[...,start:start+64,:],ref,atol=1e-6)
            z=Packed(torch.ones_like(x)*2.3,bits).decode()
            assert torch.allclose(z,torch.ones_like(x)*2.3)
    return {'rotation_inner_product_max_error':err,'packing_scalar_reference_and_constant_groups':'passed'}


def install(model, quantized):
    from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb, eager_attention_forward
    stores = {}
    def forward(self, hidden_states, position_embeddings, attention_mask=None, **kwargs):
        shape=hidden_states.shape[:-1]; hidden_shape=(*shape,-1,self.head_dim)
        q=self.q_norm(self.q_proj(hidden_states).view(hidden_shape)).transpose(1,2)
        k=self.k_norm(self.k_proj(hidden_states).view(hidden_shape)).transpose(1,2)
        v=self.v_proj(hidden_states).view(hidden_shape).transpose(1,2)
        q,k=apply_rotary_pos_emb(q,k,*position_embeddings)
        if quantized:q,k=rotate(q),rotate(k)
        history=stores.setdefault(self.layer_idx,[])
        old_k=[x[0].decode() if quantized else x[0] for x in history]
        old_v=[x[1].decode() if quantized else x[1] for x in history]
        keys=torch.cat(old_k+[k],-2); values=torch.cat(old_v+[v],-2)
        prior=keys.shape[-2]-q.shape[-2]
        row=torch.arange(q.shape[-2],device=q.device)+prior
        col=torch.arange(keys.shape[-2],device=q.device)
        mask=torch.zeros((1,1,len(row),len(col)),device=q.device,dtype=q.dtype)
        mask.masked_fill_(col[None,:]>row[:,None],torch.finfo(q.dtype).min)
        out,weights=eager_attention_forward(self,q,keys,values,mask,dropout=0.,scaling=self.scaling)
        # Current chunk is native during this read, packed only for later reads.
        bits=4 if len(history)==0 or self.layer_idx==14 else 2
        history.append((Packed(k,bits),Packed(v,bits)) if quantized else (k.detach(),v.detach()))
        return self.o_proj(out.reshape(*shape,-1).contiguous()),weights
    for layer in model.model.layers: layer.self_attn.forward=types.MethodType(forward,layer.self_attn)
    return stores


def run_qwen(tokens):
    from transformers import AutoModelForCausalLM,AutoTokenizer
    model_name='Qwen/Qwen3-0.6B'
    from huggingface_hub import snapshot_download
    local_path=snapshot_download(model_name,local_files_only=True)
    tok=AutoTokenizer.from_pretrained(local_path,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(local_path,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').eval()
    torch.set_num_threads(4)
    fixture=('Model compression reduces memory requirements. Quantization stores values with fewer bits. '
             'A useful evaluation compares numerical error, model outputs and actual storage. ')*100
    ids=tok(fixture,return_tensors='pt').input_ids[:,:tokens]
    baseline=[]
    with torch.no_grad():
        # Check that unquantized chunked attention agrees with a normal full forward pass.
        full=model(ids,use_cache=False).logits
        stores=install(model,False)
        for start in range(0,ids.shape[1],64):
            chunk=ids[:,start:start+64]
            baseline.append(model(chunk,position_ids=torch.arange(start,start+chunk.shape[1])[None,:],use_cache=False).logits)
        base=torch.cat(baseline,1)
        base_err=(base-full).abs().max().item()
        assert torch.allclose(base,full,atol=5e-4,rtol=1e-4),base_err
        native_bytes=sum(t.numel()*t.element_size() for hist in stores.values() for pair in hist for t in pair)
        stores=install(model,True); outputs=[]
        for start in range(0,ids.shape[1],64):
            chunk=ids[:,start:start+64]
            outputs.append(model(chunk,position_ids=torch.arange(start,start+chunk.shape[1])[None,:],use_cache=False).logits)
        quant=torch.cat(outputs,1)
        packed_bytes=sum(t.nbytes() for hist in stores.values() for pair in hist for t in pair)
        valid=slice(64,None) # first chunk has no compressed history
        p=base[:,valid].log_softmax(-1);q=quant[:,valid].log_softmax(-1)
        kl=(p.exp()*(p-q)).sum(-1).mean().item()
        agree=(base[:,valid].argmax(-1)==quant[:,valid].argmax(-1)).float().mean().item()
    return {'model':model_name,'tokens':ids.shape[1],'chunk_tokens':64,'dtype':'float32','device':'cpu',
        'native_chunk_vs_full_max_logit_error':base_err,'teacher_to_quantized_mean_kl':kl,
        'top1_agreement_after_first_chunk':agree,'native_cache_bytes':native_bytes,'packed_cache_bytes':packed_bytes,
        'compression_vs_fp32':native_bytes/packed_bytes,'compression_vs_hypothetical_fp16':native_bytes/2/packed_bytes,
        'limits':'repeated synthetic text smoke test; no geometry QAD, no benchmark perplexity or fused GPU speedup claim'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--qwen',action='store_true');ap.add_argument('--tokens',type=int,default=256)
    args=ap.parse_args();result={'small_tensor_tests':self_test()}
    if args.qwen:result['qwen']=run_qwen(args.tokens)
    print(json.dumps(result,indent=2))
