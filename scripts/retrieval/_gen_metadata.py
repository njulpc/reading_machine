#!/usr/bin/env python3
"""Generate metadata/2026-07/papers_index.json and keywords.csv from final list."""
import json, re, csv
from collections import Counter, defaultdict

BASE = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07"
final = json.load(open(f"{BASE}/_arxiv_raw/final.json"))

TECH_NAME = {
    "quantization": "量化", "pruning": "剪枝", "sparsity": "稀疏化",
    "distillation": "知识蒸馏", "kv_cache": "KV缓存压缩",
    "token_compression": "Token/上下文压缩", "low_rank": "低秩分解",
    "compression_other": "其他压缩", "other": "其他",
}

KW_EXTRACT = [
    ("GPTQ", r"\bGPTQ\b"), ("AWQ", r"\bAWQ\b"), ("GGUF", r"\bGGUF\b"),
    ("FP4", r"\bFP4\b|MXFP4|HiFloat4"), ("FP8", r"\bFP8\b"),
    ("INT4", r"\bINT4\b|4-bit"), ("INT8", r"\bINT8\b|8-bit"),
    ("low-bit", r"low[- ]?bit|1-bit|2-bit|two-bit|one-bit|binariz|ternar"),
    ("mixed-precision", r"mixed[- ]precision"),
    ("PTQ", r"post-training quantization|\bPTQ\b"),
    ("QAT", r"quantization-aware|\bQAT\b"),
    ("KV cache", r"KV[- ]cache|key-value cache"),
    ("vector quantization", r"vector quantiz|\bVQ\b"),
    ("LLM", r"\bLLM\b|large language model"),
    ("VLM", r"\bVLM\b|vision-language"),
    ("diffusion", r"diffusion"),
    ("edge deployment", r"edge|on-device|embedded|mobile"),
    ("FPGA", r"\bFPGA\b"),
    ("structured pruning", r"structured prun|channel prun|filter prun"),
    ("unstructured pruning", r"unstructured prun|magnitude prun"),
    ("lottery ticket", r"lottery ticket"),
    ("N:M sparsity", r"N:M sparse|2:4"),
    ("self-distillation", r"self-distill"),
    ("token pruning", r"token prun|token reduct|token merg|token compress|token condens|token select"),
    ("low-rank", r"low[- ]rank|LoRA"),
    ("fixed-point", r"fixed[- ]point|integer-only"),
    ("sparse accelerator", r"spars\w+ accelerator|sparse.{0,20}hardware|hardware.{0,20}spars"),
    ("3DGS compression", r"gaussian splatting"),
    ("semantic IDs", r"semantic id"),
    ("dataset distillation", r"dataset distill"),
    ("neuromorphic", r"neuromorphic|spiking"),
]

def extract_kws(p):
    text = p["title"] + " " + p["abstract"]
    kws = list(p.get("tech_tags", []))
    for name, pat in KW_EXTRACT:
        if re.search(pat, text, re.I):
            kws.append(name)
    seen, out = set(), []
    for k in kws:
        if k not in seen:
            seen.add(k); out.append(k)
    return out

index = {
    "collection_date": "2026-07-30",
    "date_range": "2026-07-01 ~ 2026-07-29 (UTC)",
    "query_keywords": ["quantization", "quantize", "quantized", "low-bit", "model compression",
                        "pruning", "sparsity", "knowledge distillation", "KV cache",
                        "mixed precision", "GPTQ", "AWQ", "weight compression",
                        "low precision", "post-training quantization", "model pruning",
                        "vector quantization", "sparse training", "KV cache compression"],
    "source": "arxiv.org API (export.arxiv.org)",
    "scope_note": "收录 2026-07-01 至 2026-07-29 提交、以模型压缩为核心主题的论文（量化/剪枝/稀疏/压缩向蒸馏/KV缓存压缩/Token压缩/低秩）。纯能力迁移的 on-policy/policy 蒸馏、纯 serving 系统、压缩感知与编解码论文经人工审阅后排除。",
    "total_papers": len(final),
    "papers": [],
}

kw_counter = defaultdict(list)
for p in final:
    kws = extract_kws(p)
    for k in kws:
        kw_counter[k].append(p["id"])
    hl = p["abstract"].split(". ")[0]
    if len(hl) > 150:
        hl = hl[:147] + "..."
    index["papers"].append({
        "id": p["id"],
        "title": p["title"],
        "authors": p["authors"][:8] + (["et al."] if len(p["authors"]) > 8 else []),
        "submitted": p["published"],
        "categories": p["categories"],
        "url": f"https://arxiv.org/abs/{p['id']}",
        "keywords": kws,
        "techniques": [t for t in p.get("tech_tags", [])],
        "techniques_zh": [TECH_NAME.get(t, t) for t in p.get("tech_tags", [])],
        "highlight": hl,
    })

import os
os.makedirs(f"{BASE}/metadata/2026-07", exist_ok=True)
json.dump(index, open(f"{BASE}/metadata/2026-07/papers_index.json", "w"), indent=1, ensure_ascii=False)

rows = sorted(kw_counter.items(), key=lambda kv: -len(kv[1]))
with open(f"{BASE}/metadata/2026-07/keywords.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["keyword", "occurrence", "paper_ids"])
    for k, ids in rows:
        w.writerow([k, len(ids), "|".join(sorted(set(ids)))])
print("papers:", len(final), "keywords:", len(rows))
for k, ids in rows[:15]:
    print(f"  {k}: {len(ids)}")
