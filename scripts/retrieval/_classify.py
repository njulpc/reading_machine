#!/usr/bin/env python3
"""Classify model-compression relevance with scored heuristics."""
import json, re

papers = json.load(open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/parsed.json"))

TECH = re.compile(r"quantiz|GPTQ|AWQ|QLoRA|GGUF|low[- ]?bit|bit[- ]?width|bits per weight|\bbpw\b|mixed[- ]precision|integer[- ]only|binariz|ternar|1-bit|one-bit|two-bit|\bINT[248]\b|\bFP[468]\b|\bMXFP|NVFP|prun|sparsit|sparse (model|weight|neural|network)|distill|compress|KV[- ]cache|low[- ]rank|factoriz|weight sharing|token (prun|merg|condens|reduct|compress)", re.I)

TITLE_STRONG = re.compile(r"quantiz|prun|compress|distill|sparsit|low[- ]?bit|bit[- ]?width|mixed[- ]precision|integer[- ]only|binariz|ternar|\bINT[248]\b|\bFP[468]\b|MXFP|NVFP|KV[- ]cache|slim|tiny|lightweight|compact|efficient (model|LLM|network|inference|transformer)|low[- ]rank|GPTQ|AWQ", re.I)

INTENT = re.compile(r"model compression|compress (the |a |an )?(model|network|LLM|transformer|weight)|memory footprint|memory (usage|consumption|budget|efficien)|edge device|edge deploy|on-device|deploy|inference (cost|efficien|speed|latency|accelerat)|accelerat|latency|throughput|real[- ]time|resource[- ]constrain|compact model|small(er)? model|lightweight|efficient (model|inference|deploy)|reduc(e|ing) (the )?(model |memory |comput|cost|parameter|size)|compression (ratio|rate|framework|method|technique|pipeline)|bits per weight|bitwidth|low-bit|post-training quantization|quantization-aware|pruning (method|strategy|framework|ratio|rate)|sparse (model|network|weight)|distillation (to|into) (a )?(small|compact|light|tiny)|student (model|network)", re.I)

NEG = re.compile(r"quantum (comput|circuit|simulat|field|state|chem|phys|error|machine learning model for quantum)|gauge theorr|lattice QCD|black hole|gravitat|cosmolog|image compression|video compression|codec|JPEG|H\.26|speech coding|audio coding|data compression|text compression|compression algorithm for|solar|seismic|MRI reconstruction|CT reconstruction|hyperspectral image compression", re.I)

NEG_TITLE = re.compile(r"speculative decoding|sparse attention|Mixture-of-Experts routing|MoE routing|policy distillation for|distillation for (RL|reinforcement|agent)", re.I)

def classify(p):
    t, a = p["title"], p["abstract"]
    text = t + " " + a
    score = 0
    reasons = []
    if TITLE_STRONG.search(t):
        score += 3; reasons.append("title-strong")
    if TECH.search(a):
        score += 1; reasons.append("abs-tech")
    if INTENT.search(text):
        score += 2; reasons.append("intent")
    if NEG.search(text) and not TITLE_STRONG.search(t):
        score -= 3; reasons.append("neg-domain")
    if NEG_TITLE.search(t) and not re.search(r"compress|quantiz|prun", t, re.I):
        score -= 2; reasons.append("neg-title")
    keep = score >= 3
    return keep, score, reasons

kept, dropped = [], []
for p in papers:
    keep, score, reasons = classify(p)
    p["rel_score"] = score
    p["rel_reasons"] = reasons
    (kept if keep else dropped).append(p)

print("kept:", len(kept), "dropped:", len(dropped))
json.dump(kept, open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/kept.json", "w"), indent=1, ensure_ascii=False)
json.dump(dropped, open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/dropped.json", "w"), indent=1, ensure_ascii=False)
