#!/usr/bin/env python3
"""Retrieve all model-compression-related arXiv papers submitted in 2026-03."""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://export.arxiv.org/api/query"
DATE_RANGE = "submittedDate:[202603010000+TO+202603312359]"
KEYWORDS = [
    "quantization", "quantize", "quantised", "low-bit", "model compression",
    "pruning", "sparsity", "knowledge distillation", "KV cache compression",
    "mixed precision", "GPTQ", "AWQ", "1-bit", "2-bit", "binary neural",
    "weight sharing", "network slimming", "tensor decomposition",
    "low-rank", "vector quantization", "FP4", "FP8", "INT4", "INT8",
    "KV cache", "token pruning", "early exit",
]
TARGET_CATS = {"cs.LG", "cs.CL", "cs.CV", "cs.AI", "cs.NE", "cs.AR", "cs.DC",
               "cs.IR", "cs.CR", "cs.IT", "cs.MM", "cs.SD", "eess.AS", "eess.IV", "stat.ML"}

NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

def query(search, start=0, max_results=100):
    q = f"{search}+AND+{DATE_RANGE}"
    url = f"{BASE}?search_query={urllib.parse.quote(q, safe=':[]()')}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=ascending"
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")

def parse(xml_text):
    root = ET.fromstring(xml_text)
    entries = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.strip()
        aid = aid.split("/abs/")[-1]
        aid_base = aid.split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summary = " ".join(e.find("a:summary", NS).text.split())
        published = e.find("a:published", NS).text.strip()
        updated = e.find("a:updated", NS).text.strip()
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        primary = e.find("arxiv:primary_category", NS)
        primary_cat = primary.get("term") if primary is not None else (cats[0] if cats else "")
        authors = [a.find("a:name", NS).text for a in e.findall("a:author", NS)]
        entries.append({
            "id": aid_base, "version": aid, "title": title, "abstract": summary,
            "published": published, "updated": updated,
            "categories": cats, "primary_category": primary_cat, "authors": authors,
        })
    total = root.find("opensearch:totalResults", {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"})
    total_n = int(total.text) if total is not None else 0
    return entries, total_n

papers = {}
import sys, os
start_i, end_i, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
for kw in KEYWORDS[start_i:end_i]:
    search = f"all:{urllib.parse.quote(kw)}"
    start = 0
    while True:
        try:
            xml_text = query(search, start=start)
            entries, total = parse(xml_text)
        except Exception as ex:
            print(f"[WARN] {kw} start={start}: {ex}; retry once")
            time.sleep(5)
            try:
                xml_text = query(search, start=start)
                entries, total = parse(xml_text)
            except Exception as ex2:
                print(f"[FAIL] {kw} start={start}: {ex2}")
                break
        for ent in entries:
            if ent["id"] not in papers:
                ent["hit_keywords"] = [kw]
                papers[ent["id"]] = ent
            else:
                if kw not in papers[ent["id"]]["hit_keywords"]:
                    papers[ent["id"]]["hit_keywords"].append(kw)
        print(f"{kw}: start={start} got={len(entries)} total={total}")
        if start + len(entries) >= total or not entries:
            break
        start += len(entries)
        time.sleep(1)
    time.sleep(1)

with open(f"scripts/retrieved_part_{tag}.json", "w") as f:
    json.dump(list(papers.values()), f, ensure_ascii=False)
os._exit(0)
out = []
for pid, p in papers.items():
    if not p["published"].startswith("2026-03"):
        continue
    if not set(p["categories"]) & TARGET_CATS:
        continue
    out.append(p)

out.sort(key=lambda x: x["published"])
print(f"\nTOTAL unique papers in 2026-03 hitting target cats: {len(out)}")
with open("/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-03/scripts/retrieved_2026_03_raw.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
