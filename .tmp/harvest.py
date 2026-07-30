#!/usr/bin/env python3
"""Harvest June-2026 model-compression papers from arXiv API."""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import sys

NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
DATE_RANGE = "submittedDate:[202606010000+TO+202606302359]"
CATS = "(cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.AR)"

KEYWORDS = [
    "quantization",
    "quantize",
    "low-bit",
    "model compression",
    "pruning",
    "sparsity",
    "knowledge distillation",
    "KV cache compression",
    "mixed precision",
    "GPTQ",
    "AWQ",
    "weight compression",
    "network compression",
    "model pruning",
    "sparse training",
    "binary neural network",
    "ternary",
    "post-training quantization",
]

def build_query(kw):
    kw_enc = urllib.parse.quote(f'"{kw}"')
    return f"{CATS}+AND+all:{kw_enc}+AND+{DATE_RANGE}"

def fetch(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            print(f"  fetch error ({e}), retry {i+1}", file=sys.stderr)
            time.sleep(45)
    return None

def parse_feed(data):
    root = ET.fromstring(data)
    total = root.find("opensearch:totalResults", {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"})
    total = int(total.text) if total is not None else 0
    entries = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.strip()
        base = aid.split("/abs/")[-1]
        base_nov = base.split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summary = " ".join(e.find("a:summary", NS).text.split())
        published = e.find("a:published", NS).text
        updated = e.find("a:updated", NS).text
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        prim = e.find("arxiv:primary_category", NS)
        authors = [a.find("a:name", NS).text for a in e.findall("a:author", NS)]
        comment = e.find("arxiv:comment", NS)
        entries.append({
            "id": base_nov, "version": base, "title": title, "summary": summary,
            "published": published, "updated": updated, "categories": cats,
            "primary_category": prim.get("term") if prim is not None else None,
            "authors": authors,
            "comment": comment.text if comment is not None else None,
        })
    return total, entries

def main():
    import os
    if os.path.exists(sys.argv[1]):
        d = json.load(open(sys.argv[1]))
        papers = d["papers"]; kw_hits = d["keyword_hits"]
        print(f"resuming with {len(papers)} papers, {len(kw_hits)} keywords done", flush=True)
    else:
        papers = {}
        kw_hits = {}
    for kw in KEYWORDS:
        if kw in kw_hits:
            continue
        q = build_query(kw)
        start = 0
        page = 100
        kw_ids = set()
        kw_ok = True
        while True:
            url = f"https://export.arxiv.org/api/query?search_query={q}&start={start}&max_results={page}"
            data = fetch(url)
            if data is None:
                print(f"FAILED kw={kw} start={start}", file=sys.stderr)
                kw_ok = False
                break
            total, entries = parse_feed(data)
            if start == 0:
                print(f"[{kw}] total={total}")
            for ent in entries:
                kw_ids.add(ent["id"])
                if ent["id"] not in papers:
                    papers[ent["id"]] = ent
            start += page
            if start >= total or not entries:
                break
            time.sleep(8)
        if kw_ok:
            kw_hits[kw] = sorted(kw_ids)
        with open(sys.argv[1], "w") as f:
            json.dump({"papers": papers, "keyword_hits": kw_hits}, f, ensure_ascii=False, indent=1)
        print(f"  saved, cumulative unique={len(papers)}", flush=True)
        time.sleep(8)
    out = {"papers": papers, "keyword_hits": kw_hits}
    with open(sys.argv[1], "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\nTOTAL unique papers: {len(papers)}")

if __name__ == "__main__":
    main()
