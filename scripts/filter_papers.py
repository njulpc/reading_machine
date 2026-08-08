#!/usr/bin/env python3
"""Fetch arXiv paper metadata and filter by model compression keywords."""
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import re
import json
import time
import sys
from datetime import datetime

# Keywords for model compression relevance
KEYWORDS = [
    "quantization", "quantize", "quantized", "low-bit", "low bit",
    "model compression", "compress", "compressed", "compression",
    "pruning", "prune", "pruned", "sparsity", "sparse",
    "knowledge distillation", "distillation", "distilled",
    "KV cache", "kv-cache", "kv cache",
    "mixed precision",
    "GPTQ", "AWQ", "GGUF", "GGML",
    "INT4", "INT8", "FP4", "FP8", "NF4", "MXFP",
    "post-training quantization", "PTQ",
    "quantization-aware", "QAT",
    "weight quantization", "activation quantization",
    "block quantization", "group-wise",
    "bit", "bits", "bitwidth",
    "efficient inference", "inference efficiency",
    "edge deployment", "mobile deployment",
]

def fetch_paper_metadata(arxiv_ids):
    """Batch fetch metadata for given arXiv IDs."""
    ids_str = ",".join(arxiv_ids)
    url = f"http://export.arxiv.org/api/query?id_list={ids_str}&max_results={len(arxiv_ids)}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8")
        return data
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  Rate limited, waiting 10s...")
            time.sleep(10)
            return fetch_paper_metadata(arxiv_ids)
        print(f"  HTTP error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def parse_metadata(xml_text):
    """Parse arXiv Atom feed into paper dicts."""
    papers = []
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"XML parse error: {e}")
        return papers
    
    for entry in root.findall("atom:entry", ns):
        title_elem = entry.find("atom:title", ns)
        title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
        
        summary_elem = entry.find("atom:summary", ns)
        abstract = summary_elem.text.strip() if summary_elem is not None else ""
        
        id_elem = entry.find("atom:id", ns)
        arxiv_id = ""
        if id_elem is not None:
            m = re.search(r'arxiv\.org/abs/(.+)', id_elem.text)
            if m:
                arxiv_id = m.group(1)
        
        published_elem = entry.find("atom:published", ns)
        published = published_elem.text[:10] if published_elem is not None else ""
        
        updated_elem = entry.find("atom:updated", ns)
        updated = updated_elem.text[:10] if updated_elem is not None else ""
        
        authors = []
        for author in entry.findall("atom:author", ns):
            name_elem = author.find("atom:name", ns)
            if name_elem is not None:
                authors.append(name_elem.text)
        
        categories = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term", "")
            if term:
                categories.append(term)
        
        prim_cat = entry.find("arxiv:primary_category", ns)
        primary_category = prim_cat.get("term", "") if prim_cat is not None else ""
        
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "published": published,
            "updated": updated,
            "categories": categories,
            "primary_category": primary_category,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        })
    
    return papers

def score_relevance(paper):
    """Score paper relevance to model compression (0-1)."""
    text = f"{paper['title']} {paper['abstract']}".lower()
    
    matches = 0
    title_matches = 0
    for kw in KEYWORDS:
        kw_lower = kw.lower()
        if kw_lower in text:
            matches += 1
        if kw_lower in paper['title'].lower():
            title_matches += 2
    
    score = (matches + title_matches) / (len(KEYWORDS) + 4)
    return min(score, 1.0)

def main():
    # Read IDs from stdin (one per line, format "arXiv:2608.xxxxx" or just "2608.xxxxx")
    raw_ids = []
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            raw_ids = [l.strip() for l in f if l.strip()]
    else:
        raw_ids = [l.strip() for l in sys.stdin if l.strip()]
    
    # Clean IDs
    all_ids = []
    for rid in raw_ids:
        rid = rid.replace("arXiv:", "").strip()
        if re.match(r'^\d{4,5}\.\d{4,5}$', rid):
            all_ids.append(rid)
    
    all_ids = list(dict.fromkeys(all_ids))  # preserve order, remove duplicates
    print(f"Total unique IDs: {len(all_ids)}")
    
    target_date = "2026-08-07"
    
    # Batch fetch (arXiv API supports up to ~200 IDs per request)
    all_papers = []
    batch_size = 50
    for i in range(0, len(all_ids), batch_size):
        batch = all_ids[i:i+batch_size]
        print(f"Fetching batch {i//batch_size + 1}/{(len(all_ids)-1)//batch_size + 1} ({len(batch)} papers)...")
        xml = fetch_paper_metadata(batch)
        if xml:
            papers = parse_metadata(xml)
            all_papers.extend(papers)
            print(f"  Got {len(papers)} papers")
        time.sleep(5)  # rate limit
    for i in range(0, len(all_ids), batch_size):
        batch = all_ids[i:i+batch_size]
        print(f"Fetching batch {i//batch_size + 1}/{(len(all_ids)-1)//batch_size + 1} ({len(batch)} papers)...")
        xml = fetch_paper_metadata(batch)
        if xml:
            papers = parse_metadata(xml)
            all_papers.extend(papers)
            print(f"  Got {len(papers)} papers")
        time.sleep(3)  # rate limit
    
    print(f"\nTotal papers fetched: {len(all_papers)}")
    
    # Filter by date and relevance
    filtered = []
    for p in all_papers:
        # Check if published on target date
        if p["published"] != target_date and p["updated"] != target_date:
            continue
        
        score = score_relevance(p)
        p["relevance_score"] = round(score, 4)
        
        if score >= 0.05:  # minimum threshold
            filtered.append(p)
    
    filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    print(f"\n=== Model Compression Papers for {target_date} ===")
    print(f"Found {len(filtered)} relevant papers\n")
    
    for p in filtered:
        print(f"[{p['arxiv_id']}] (score: {p['relevance_score']})")
        print(f"  Title: {p['title']}")
        print(f"  Authors: {', '.join(p['authors'][:3])}{'...' if len(p['authors'])>3 else ''}")
        print(f"  Categories: {', '.join(p['categories'])}")
        print(f"  Abstract: {p['abstract'][:300]}...")
        print()
    
    # Save
    output = {
        "date": target_date,
        "total_checked": len(all_papers),
        "filtered_count": len(filtered),
        "papers": filtered
    }
    
    with open(f"papers/arxiv_filtered_{target_date}.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to papers/arxiv_filtered_{target_date}.json")

if __name__ == "__main__":
    main()
