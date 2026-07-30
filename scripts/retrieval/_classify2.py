#!/usr/bin/env python3
"""Second-pass strict relevance: auto-keep / auto-drop / borderline."""
import json, re

papers = json.load(open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/kept.json"))

HARD_TECH_TITLE = re.compile(
    r"quantiz|GPTQ|AWQ|GGUF|low[- ]?bit|bit[- ]?width|mixed[- ]precision|integer[- ]only|"
    r"binariz|ternar|\bINT[248]\b|\bFP[468]\b|MXFP|NVFP|MXAttention|prun|sparsif|"
    r"compress(ion|ing|ed)? (of|for|the|a|an)? ?(model|LLM|language model|network|transformer|weight|neural|MoE|diffusion|VLM|encoder)|"
    r"model compression|weight compression|KV[- ]cache (compress|quant|evict|prun|reduc|merg|optim)|"
    r"distill", re.I)

KV_TITLE = re.compile(r"KV[- ]cache", re.I)

# distillation kept only with efficiency/compression intent in title or abstract
KD_EFF = re.compile(r"small|compact|tiny|lightweight|efficient|edge|on-device|deploy|compress|resource|latency|memory|footprint|budget|mobile|embedded|accelerat|slim|1\.?\d*\s?(x|×) smaller|parameter-efficien", re.I)

DROP_DOMAIN = re.compile(r"compressed sensing|spectrometer|meta[- ]?surface|metasurface|optical|photonic|MRI|seismic|hyperspectral|codec|video coding|image coding|watermark|steganograph|federated.*(privacy|attack)|backdoor|adversarial attack|jailbreak", re.I)

DROP_TITLE = re.compile(r"on-policy distillation|policy distillation|self-distillation for|distillation for (reasoning|agents?|RL|alignment|evaluation|tutor)|speculative decoding|beam search|routing|scheduling|serving system|threat|attack|stealth|forg|inject", re.I)

auto_keep, auto_drop, border = [], [], []
for p in papers:
    t, a = p["title"], p["abstract"]
    text = t + " " + a
    is_kd = re.search(r"distill", t, re.I)
    if DROP_DOMAIN.search(text) and not HARD_TECH_TITLE.search(t):
        p["verdict"] = "drop:domain"; auto_drop.append(p); continue
    if is_kd and not KD_EFF.search(text):
        p["verdict"] = "drop:kd-no-efficiency"; auto_drop.append(p); continue
    if DROP_TITLE.search(t) and not re.search(r"quantiz|prun|compress", t, re.I):
        p["verdict"] = "drop:title"; auto_drop.append(p); continue
    if HARD_TECH_TITLE.search(t):
        p["verdict"] = "keep:title"; auto_keep.append(p); continue
    if KV_TITLE.search(t) and re.search(r"compress|quant|evict|prun|reduc|merg|spars|budget|optim", t, re.I):
        p["verdict"] = "keep:kv"; auto_keep.append(p); continue
    # abstract-level strong: compression is clearly the topic
    if re.search(r"we (propose|present|introduce).{0,120}(quantiz|prun|compress|distill)", a, re.I) and KD_EFF.search(text):
        p["verdict"] = "keep:abstract"; auto_keep.append(p); continue
    p["verdict"] = "borderline"; border.append(p)

print("auto_keep:", len(auto_keep), "auto_drop:", len(auto_drop), "borderline:", len(border))
json.dump(auto_keep, open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/keep2.json", "w"), indent=1, ensure_ascii=False)
json.dump(auto_drop, open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/drop2.json", "w"), indent=1, ensure_ascii=False)
json.dump(border, open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/border.json", "w"), indent=1, ensure_ascii=False)
