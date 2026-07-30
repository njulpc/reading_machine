#!/usr/bin/env python3
"""Retrieve 2026-03 model-compression papers from arXiv with conservative pacing."""
import json, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

BASE = "https://export.arxiv.org/api/query"
DR = "submittedDate:[202603010000+TO+202603312359]"
CATS = "(cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.AR+OR+cat:cs.DC+OR+cat:cs.IR+OR+cat:cs.MM+OR+cat:cs.IT+OR+eess.AS+OR+eess.IV+OR+stat.ML)"
QUERIES = {
    "quant": "(all:quantization+OR+all:quantize+OR+all:quantised+OR+all:low-bit+OR+all:GPTQ+OR+all:AWQ+OR+all:FP4+OR+all:FP8+OR+all:INT4+OR+all:INT8+OR+all:%22mixed+precision%22+OR+all:%22vector+quantization%22+OR+all:%22binary+neural%22)",
    "prune": "(all:pruning+OR+all:sparsity+OR+all:%22model+compression%22+OR+all:%22network+slimming%22+OR+all:%22tensor+decomposition%22+OR+all:%22low-rank%22+OR+all:%22token+pruning%22+OR+all:%22early+exit%22+OR+all:%22weight+sharing%22)",
    "distill": "(all:%22knowledge+distillation%22+OR+all:%22KV+cache%22+OR+all:%221-bit%22+OR+all:%222-bit%22+OR+all:%22speculative+decoding%22+OR+all:%22model+compression%22+OR+all:slimming)",
}
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom",
      "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}

def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0 (mailto:research@example.com)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8")
        except Exception as ex:
            wait = 60 * (i + 1)
            print(f"  retry {i+1} after {wait}s: {ex}", flush=True)
            time.sleep(wait)
    raise RuntimeError("failed: " + url)

def parse(xml_text):
    root = ET.fromstring(xml_text)
    entries = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.strip().split("/abs/")[-1]
        entries.append({
            "id": aid.split("v")[0], "version": aid,
            "title": " ".join(e.find("a:title", NS).text.split()),
            "abstract": " ".join(e.find("a:summary", NS).text.split()),
            "published": e.find("a:published", NS).text.strip(),
            "updated": e.find("a:updated", NS).text.strip(),
            "categories": [c.get("term") for c in e.findall("a:category", NS)],
            "primary_category": (e.find("arxiv:primary_category", NS).get("term")
                                 if e.find("arxiv:primary_category", NS) is not None else ""),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
        })
    t = root.find("opensearch:totalResults", NS)
    return entries, int(t.text) if t is not None else 0

papers = {}
for tag, kq in QUERIES.items():
    start = 0
    while True:
        url = f"{BASE}?search_query={CATS}+AND+{kq}+AND+{DR}&start={start}&max_results=100&sortBy=submittedDate&sortOrder=ascending"
        xml_text = fetch(url)
        entries, total = parse(xml_text)
        for ent in entries:
            if ent["id"] in papers:
                if tag not in papers[ent["id"]]["hits"]:
                    papers[ent["id"]]["hits"].append(tag)
            else:
                ent["hits"] = [tag]
                papers[ent["id"]] = ent
        print(f"{tag}: start={start} got={len(entries)} total={total}", flush=True)
        if start + len(entries) >= total or not entries:
            break
        start += 100
        time.sleep(5)
    time.sleep(5)

out = sorted(papers.values(), key=lambda x: x["published"])
with open("scripts/retrieved_2026_03_raw.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("TOTAL:", len(out))
