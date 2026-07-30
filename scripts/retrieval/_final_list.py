#!/usr/bin/env python3
"""Final paper list: auto_keep + manual borderline decisions; spot-check outputs."""
import json, re

base = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw"
auto_keep = json.load(open(f"{base}/keep2.json"))
border = json.load(open(f"{base}/border.json"))

BORDER_KEEP = {
"2607.00780","2607.03246","2607.03652","2607.05445","2607.03760","2607.04302",
"2607.04171","2607.05457","2607.04531","2607.05711","2607.06217","2607.06173",
"2607.06827","2607.06841","2607.07144","2607.06922","2607.08015","2607.08771",
"2607.08754","2607.09385","2607.10611","2607.10784","2607.11990","2607.12505",
"2607.13205","2607.13735","2607.13770","2607.14327","2607.16339","2607.14557",
"2607.15846","2607.15563","2607.16624","2607.17099","2607.18081","2607.19431",
"2607.17486","2607.19575","2607.20125","2607.20357","2607.21291","2607.22790",
"2607.24841","2607.22038","2607.22389","2607.23265","2607.24568","2607.24555",
"2607.25527","2607.25180","2607.25504","2607.25545","2607.25669","2607.26515",
"2607.27031","2607.26648",
}

final = list(auto_keep)
for p in border:
    if p["id"] in BORDER_KEEP:
        p["verdict"] = "keep:manual"
        final.append(p)

final.sort(key=lambda x: (x["published"], x["id"]))
print("final count:", len(final))
json.dump(final, open(f"{base}/final.json", "w"), indent=1, ensure_ascii=False)

# category tagging
def tag(p):
    text = (p["title"] + " " + p["abstract"]).lower()
    tags = []
    if re.search(r"quantiz|gptq|awq|gguf|low[- ]?bit|bit[- ]?width|mixed[- ]precision|integer[- ]only|binariz|ternar|int[248]\b|fp[468]\b|mxfp|nvfp|fixed[- ]point|bit[- ]serial|hifloat|low[- ]precision|fp4|fp8", text):
        tags.append("quantization")
    if re.search(r"prun|lottery ticket", text):
        tags.append("pruning")
    if re.search(r"sparsit|sparsif|n:m sparse|compute skipping|neuron loading", text):
        tags.append("sparsity")
    if re.search(r"distill", text):
        tags.append("distillation")
    if re.search(r"kv[- ]cache|kv cache|key[- ]value cache", text) and re.search(r"compress|quant|evict|prun|reduc|merg|spars|summar|filter", text):
        tags.append("kv_cache")
    if re.search(r"token (compress|prun|merg|reduct|condens|select)|context compress|token[- ]compute", text):
        tags.append("token_compression")
    if re.search(r"low[- ]rank|tensor train|factoriz", text):
        tags.append("low_rank")
    if re.search(r"compress", text) and not tags:
        tags.append("compression_other")
    return tags or ["other"]

from collections import Counter
c = Counter()
for p in final:
    p["tech_tags"] = tag(p)
    for t in p["tech_tags"]:
        c[t] += 1
print(c)
json.dump(final, open(f"{base}/final.json", "w"), indent=1, ensure_ascii=False)
