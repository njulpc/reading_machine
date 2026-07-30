#!/usr/bin/env python3
"""Collect all model-compression-related arXiv papers submitted in 2026-01.

Queries the arXiv API with many keyword combinations over the full month,
dedupes by arXiv id, and saves the raw candidate pool as JSON.
"""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import sys

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}

DATE_RANGE = "submittedDate:[202601010000 TO 202601312359]"

# Keyword queries covering the required vocabulary. Each is ANDed with the
# submitted-date range. Phrases are quoted for the arXiv query language.
QUERIES = [
    'all:quantization',
    'all:quantize',
    'all:quantized',
    'all:"low-bit"',
    'all:"model compression"',
    'all:pruning',
    'all:sparsity',
    'all:"knowledge distillation"',
    'all:"KV cache"',
    'all:"mixed precision"',
    'all:GPTQ',
    'all:AWQ',
    'all:"weight compression"',
    'all:"network compression"',
    'all:"model pruning"',
    'all:distillation AND (all:LLM OR all:"language model" OR all:transformer)',
    'all:"low precision" AND (all:LLM OR all:transformer OR all:"neural network")',
    'all:"binary neural network" OR all:"binarized"',
    'all:"1-bit" AND (all:LLM OR all:"language model")',
    'all:"sparse training" OR all:"sparse inference"',
]

BASE = "https://export.arxiv.org/api/query"


def fetch(query, start, max_results=200):
    params = {
        "search_query": f"({query}) AND {DATE_RANGE}",
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            wait = 45 * (attempt + 1)
            print(f"  retry {attempt} after error: {e}; sleep {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None


def parse_feed(xml_text):
    root = ET.fromstring(xml_text)
    total = root.find("opensearch:totalResults", NS)
    total = int(total.text) if total is not None else 0
    entries = []
    for e in root.findall("atom:entry", NS):
        aid = e.find("atom:id", NS).text
        title = " ".join(e.find("atom:title", NS).text.split())
        summary = " ".join(e.find("atom:summary", NS).text.split())
        published = e.find("atom:published", NS).text
        updated = e.find("atom:updated", NS).text
        cats = [c.get("term") for c in e.findall("atom:category", NS)]
        authors = [a.find("atom:name", NS).text for a in e.findall("atom:author", NS)]
        arxiv_id = aid.split("/abs/")[-1]
        entries.append({
            "id": arxiv_id,
            "base_id": arxiv_id.split("v")[0],
            "title": title,
            "summary": summary,
            "published": published,
            "updated": updated,
            "categories": cats,
            "authors": authors,
        })
    return total, entries


def main():
    qi0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    qi1 = int(sys.argv[2]) if len(sys.argv) > 2 else len(QUERIES)
    suffix = sys.argv[3] if len(sys.argv) > 3 else ""
    pool = {}
    for q in QUERIES[qi0:qi1]:
        start = 0
        while True:
            xml = fetch(q, start)
            if xml is None:
                print(f"FAILED query {q} at start {start}", file=sys.stderr)
                break
            total, entries = parse_feed(xml)
            for e in entries:
                # keep v1 info; later versions of same paper get merged
                key = e["base_id"]
                if key not in pool:
                    pool[key] = e
            print(f"query={q!r} start={start} got={len(entries)} total={total} pool={len(pool)}")
            start += len(entries)
            if start >= total or not entries:
                break
            time.sleep(6)
        time.sleep(6)

    # filter to papers whose *original* submission (published) is in 2026-01
    jan = {}
    for k, e in pool.items():
        if e["published"].startswith("2026-01"):
            jan[k] = e
        else:
            print(f"drop (not Jan): {k} published={e['published']} {e['title'][:60]}")
    out = sorted(jan.values(), key=lambda x: x["id"])
    with open(f"candidate_pool{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nTOTAL unique Jan-2026 candidates: {len(out)}")


if __name__ == "__main__":
    main()
