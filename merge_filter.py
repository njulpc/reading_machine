#!/usr/bin/env python3
"""Merge API keyword pool + listing metadata, filter v1-in-Jan-2026,
score relevance to neural model compression, dump review TSV."""
import json
import re

api_pool = {e["base_id"]: e for e in json.load(open("api_pool.json"))}
listing_meta = json.load(open("listing_meta.json"))
listing_cand = {p["id"]: p for p in json.load(open("listing_candidates.json"))}

merged = dict(listing_meta)
for k, e in api_pool.items():
    merged[k] = e  # api entries already have full metadata

STRONG = re.compile(
    r"quantiz|prun|spars|distill|compress|low[- ]?bit|bit[- ]?width|binariz|ternar|"
    r"kv[ -]?cache|mixed[- ]precision|gptq|awq|\bint2\b|\bint4\b|\bint8\b|\bfp4\b|\bfp8\b|"
    r"weight[- ]sharing|low[- ]rank|one[- ]bit|two[- ]bit|four[- ]bit|1[- ]bit|2[- ]bit|4[- ]bit|"
    r"knowledge transfer|slimmable|tensor train|tensor decomposition|cp decomposition",
    re.I)
MLCTX = re.compile(
    r"neural|network|transformer|\bllm\b|language model|deep |deep-|model|attention|"
    r"\bcnn\b|\bvit\b|diffusion|\bbert\b|\bgpt\b|\bmlp\b|conv|encoder|decoder|embedding|"
    r"inference|fine[- ]?tun|downstream|token|classifier|backbone|generative|"
    r"machine learning|reinforcement|segmentation|detection|recognition|forecast|"
    r"recommend|speech|image|video|multimodal|vision|pre-?train|representation",
    re.I)

rows = []
for k, e in merged.items():
    if not e.get("published", "").startswith("2026-01"):
        continue
    text = e["title"] + " " + e.get("summary", "")
    strong = len(STRONG.findall(text))
    ml = len(MLCTX.findall(text))
    rows.append({
        "id": k, "title": e["title"], "strong": strong, "ml": ml,
        "cats": ",".join(e.get("categories", [])),
        "published": e["published"][:10],
        "in_api": k in api_pool, "in_listing": k in listing_cand,
    })

rows.sort(key=lambda r: (-r["strong"], r["id"]))
with open("review.tsv", "w") as f:
    f.write("id\tstrong\tml\tapi\tlst\tcats\tpublished\ttitle\n")
    for r in rows:
        f.write(f"{r['id']}\t{r['strong']}\t{r['ml']}\t{int(r['in_api'])}\t{int(r['in_listing'])}\t{r['cats']}\t{r['published']}\t{r['title']}\n")
print("rows:", len(rows))
print("strong>=1 & ml>=1:", sum(1 for r in rows if r["strong"] >= 1 and r["ml"] >= 1))
