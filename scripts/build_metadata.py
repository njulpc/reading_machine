#!/usr/bin/env python3
"""Build metadata/2026-03/papers_index.json + keywords.csv from
papers/2026-03/*/tech_analysis.md + scripts/candidates.json (arXiv metadata).
Also prints category statistics used by the monthly report (single source of truth).
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers" / "2026-03"
META_OUT = ROOT / "metadata" / "2026-03"

CAND = {p["id"]: p for p in json.loads((ROOT / "scripts" / "candidates.json").read_text())}
for extra in ("scripts/retrieved_2026_03_raw.json", "scripts/recall_check_ti.json"):
    for p in json.loads((ROOT / extra).read_text()):
        CAND.setdefault(p["id"], p)

TECH_RULES = [  # (technique_tag, [regex patterns]) — priority order
    ("early-exit", [r"early[- ]exit", r"early exiting"]),
    ("token-pruning", [r"token prun", r"token reduc", r"token merg", r"visual token", r"token compression", r"token select"]),
    ("kv-cache", [r"kv[- ]cache", r"key-value cache", r"kvcache", r"key/value cache"]),
    ("quantization", [r"quantiz", r"quanto", r"low[- ]bit", r"bitwidth", r"gptq", r"awq", r"\bfp4\b", r"\bint[248]\b",
                      r"ternary", r"binariz", r"[1248]-bit", r"mxfp", r"mixed[- ]precision quant"]),
    ("distillation", [r"distill"]),
    ("pruning", [r"prun"]),
    ("sparsity", [r"spars"]),
    ("compression", [r"compress"]),
]

KW_VOCAB = [
    ("quantization", r"quantiz"), ("PTQ", r"\bptq\b|post[- ]training quant"), ("QAT", r"\bqat\b|quantization[- ]aware"),
    ("low-bit", r"low[- ]bit|[1248]-bit|\bint[248]\b|\bfp4\b|ternary|binariz"),
    ("mixed-precision", r"mixed[- ]precision"), ("rotation/Hadamard", r"hadamard|rotation|fwht"),
    ("KV cache", r"kv[- ]cache|key-value cache|kvcache"), ("long-context", r"long[- ]context"),
    ("pruning", r"prun"), ("structured pruning", r"structured prun|channel prun|layer prun|depth prun"),
    ("token pruning", r"token prun|token reduc|token merg|visual token"),
    ("sparsity", r"spars"), ("distillation", r"distill"), ("early exit", r"early[- ]exit"),
    ("LLM", r"\bllm\b|large language model"), ("VLM/MLLM", r"\bvlm\b|\bmllm\b|vision[- ]language|visual language|multimodal"),
    ("video", r"video"), ("speech/audio", r"speech|audio"), ("diffusion", r"diffusion"),
    ("reasoning", r"reasoning"), ("MoE", r"\bmoe\b|mixture[- ]of[- ]experts"),
    ("edge deployment", r"edge deploy|on[- ]device|edge device|mobile deploy"),
    ("FPGA/hardware", r"\bfpga\b|hardware[- ]aware|hardware accelerator|\bnpu\b|\bgpu\b kernel"),
    ("LoRA/PEFT", r"\blora\b|peft|parameter[- ]efficient"),
    ("speculative decoding", r"speculative decod|speculative decoding"),
    ("activation quantization", r"activation quant"), ("weight quantization", r"weight quant|weight[- ]only quant"),
    ("outlier", r"outlier"), ("saliency", r"salien"), ("calibration", r"calibrat"),
    ("embedding", r"embedding"), ("recommendation", r"recommend"), ("RAG", r"\brag\b|retrieval[- ]augmented"),
    ("agent", r"\bagent"), ("reward", r"reward model"), ("federated", r"federated"),
    ("GPTQ", r"\bgptq\b"), ("AWQ", r"\bawq\b"), ("GGUF/llama.cpp", r"gguf|llama\.cpp"),
]

MODEL_RE = re.compile(
    r"(LLaMA[- ]?\d(?:\.\d)?[- ]?\d*G?B?|Llama[- ]?\d(?:[\- ]\d+B)?|Qwen[23]?(?:\.\d)?[- ]?\d*\.?\d*B?|"
    r"Mistral[- ]?\d*B?|DeepSeek[- ]?\w*[- ]?\d*B?|Gemma[- ]?\d+B?|Phi[- ]?\d|GPT[- ]?\d\w*|"
    r"ViT[- ]?\w*|CLIP|Whisper|Stable Diffusion|SDXL|Flux|Wan[- ]?\d\.\d|Hunyuan\w*|LLaVA[- ]?\w*|InternVL\w*)",
    re.IGNORECASE)


def extract_summary(text):
    m = re.search(r"\*\*一句话总结\*\*[：:]\s*(.+)", text)
    return m.group(1).strip() if m else ""


def classify(text):
    tags = []
    for tag, pats in TECH_RULES:
        if any(re.search(p, text, re.I) for p in pats):
            tags.append(tag)
    return tags or ["compression"]


def category_of(tags, text):
    """Primary report category."""
    has_q = "quantization" in tags
    if "early-exit" in tags:
        return "early-exit"
    if "token-pruning" in tags:
        return "token-pruning"
    if "kv-cache" in tags:
        return "kv-cache-quant" if has_q else "kv-cache-compress"
    if has_q:
        return "quantization"
    if "distillation" in tags:
        return "distillation"
    return "pruning-sparsity"


def keywords_of(text):
    kws = [name for name, pat in KW_VOCAB if re.search(pat, text, re.I)]
    return kws[:8]


def target_model_of(abstract, analysis):
    for src in (analysis, abstract):
        m = MODEL_RE.search(src or "")
        if m:
            return m.group(0)
    return ""


def main():
    papers = []
    missing = []
    for d in sorted(PAPERS.iterdir()):
        if not d.is_dir():
            continue
        pid = d.name
        md = (d / "tech_analysis.md").read_text(encoding="utf-8")
        cand = CAND.get(pid)
        if cand is None:
            missing.append(pid)
            cand = {}
        title = cand.get("title") or re.search(r"^# 深度技术分析：(.+)$", md, re.M).group(1).strip()
        abstract = cand.get("abstract", "")
        basis = title + " " + abstract  # primary classification uses title+abstract only
        tags = classify(basis)
        cat = category_of(tags, basis)
        papers.append({
            "id": pid,
            "title": title,
            "authors": cand.get("authors", []),
            "submitted": (cand.get("published") or "")[:10],
            "categories": cand.get("categories", []),
            "url": f"https://arxiv.org/abs/{pid}",
            "keywords": keywords_of(basis + " " + md),
            "techniques": tags,
            "category": cat,
            "target_model": target_model_of(abstract, md),
            "highlight": extract_summary(md),
        })

    index = {
        "collection_date": "2026-03",
        "date_range": "2026-03-01 ~ 2026-03-31",
        "query_keywords": ["quantization", "pruning", "distillation", "model compression",
                           "KV cache", "efficient inference"],
        "source": "arxiv.org",
        "total_papers": len(papers),
        "retrieval_funnel": {"raw_hits": 983, "keyword_filtered_candidates": 362,
                             "deep_analyzed": len(papers)},
        "papers": papers,
    }
    META_OUT.mkdir(parents=True, exist_ok=True)
    (META_OUT / "papers_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    kw_map = defaultdict(list)
    for p in papers:
        for kw in p["keywords"]:
            kw_map[kw].append(p["id"])
    with open(META_OUT / "keywords.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "occurrence", "paper_ids"])
        for kw, ids in sorted(kw_map.items(), key=lambda kv: -len(kv[1])):
            w.writerow([kw, len(ids), "|".join(ids)])

    print("total:", len(papers), " missing-from-candidates:", missing)
    print("category counts:", dict(Counter(p["category"] for p in papers)))
    print("top keywords:", [(k, len(v)) for k, v in
                           sorted(kw_map.items(), key=lambda kv: -len(kv[1]))[:12]])


if __name__ == "__main__":
    main()
