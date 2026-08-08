#!/usr/bin/env python3
"""Parse arXiv new-list HTML to extract paper titles and filter by keywords."""
import urllib.request
import urllib.error
import re
import time
import json
from html.parser import HTMLParser

KEYWORDS = [
    "quantization", "quantize", "quantized", "low-bit", "low bit",
    "model compression", "compress", "compressed", "compression",
    "pruning", "prune", "pruned", "sparsity", "sparse",
    "knowledge distillation", "distillation", "distilled",
    "KV cache", "kv-cache", "kv cache", "kv-cache",
    "mixed precision",
    "GPTQ", "AWQ", "GGUF", "GGML",
    "INT4", "INT8", "FP4", "FP8", "NF4", "MXFP",
    "post-training quantization", "PTQ",
    "quantization-aware", "QAT",
    "weight quantization", "activation quantization",
    "block quantization", "group-wise",
    "efficient inference", "inference efficiency",
    "edge deployment", "mobile deployment",
    "one-bit", "1-bit", "2-bit", "3-bit", "4-bit", "8-bit",
]

CATEGORIES = ["cs.LG", "cs.CL", "cs.CV"]

def fetch_list_html(category):
    url = f"https://arxiv.org/list/{category}/new"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching {category}: {e}")
        return None

def fetch_abstract(arxiv_id):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
        # Extract abstract
        m = re.search(r'<blockquote class="abstract mathjax">\s*<span class="descriptor">Abstract:</span>(.*?)</blockquote>', html, re.DOTALL)
        if m:
            abstract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            return abstract
        return ""
    except Exception as e:
        print(f"  Error fetching abstract for {arxiv_id}: {e}")
        return ""

def parse_papers_from_html(html, category):
    """Parse arXiv list HTML to extract paper ID and title."""
    papers = []
    
    # Find all <dl> entries (each contains one paper)
    # Each paper block starts with <dt> and has <dd> for title/authors
    dl_blocks = re.findall(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', html, re.DOTALL)
    
    for dt_block, dd_block in dl_blocks:
        # Extract arXiv ID
        id_match = re.search(r'arXiv:(\d{4,5}\.\d{4,5})', dt_block)
        if not id_match:
            continue
        arxiv_id = id_match.group(1)
        
        # Extract title
        title_match = re.search(r"<div class='list-title mathjax'>.*?Title:</span>(.*?)</div>", dd_block, re.DOTALL)
        if not title_match:
            continue
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        
        # Extract authors
        authors_match = re.search(r"<div class='list-authors'>.*?</div>", dd_block, re.DOTALL)
        authors = []
        if authors_match:
            authors_html = authors_match.group(0)
            authors = re.findall(r'<a[^>]*>([^<]+)</a>', authors_html)
        
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "category": category,
        })
    
    return papers

def is_relevant(paper):
    text = f"{paper['title']}".lower()
    for kw in KEYWORDS:
        if kw.lower() in text:
            return True, kw
    return False, ""

def main():
    all_papers = []
    for cat in CATEGORIES:
        print(f"Fetching {cat}...")
        html = fetch_list_html(cat)
        if html:
            papers = parse_papers_from_html(html, cat)
            all_papers.extend(papers)
            print(f"  Found {len(papers)} papers in {cat}")
    
    # Deduplicate by arxiv_id
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique_papers.append(p)
    
    print(f"\nTotal unique papers: {len(unique_papers)}")
    
    # Filter by relevance
    relevant = []
    for p in unique_papers:
        rel, matched_kw = is_relevant(p)
        if rel:
            p["matched_keyword"] = matched_kw
            relevant.append(p)
    
    print(f"Relevant papers by title: {len(relevant)}")
    
    # Fetch abstracts for relevant papers
    for i, p in enumerate(relevant):
        print(f"\n[{i+1}/{len(relevant)}] Fetching abstract for {p['arxiv_id']}...")
        abstract = fetch_abstract(p["arxiv_id"])
        p["abstract"] = abstract
        time.sleep(1)  # rate limit
    
    # Final filtering with abstract
    final = []
    for p in relevant:
        text = f"{p['title']} {p.get('abstract', '')}".lower()
        matches = [kw for kw in KEYWORDS if kw.lower() in text]
        p["keywords"] = matches
        if len(matches) >= 1:
            final.append(p)
    
    print(f"\n=== FINAL: {len(final)} model compression papers ===")
    for p in final:
        print(f"\n[{p['arxiv_id']}] {p['title']}")
        print(f"  Authors: {', '.join(p['authors'][:3])}{'...' if len(p['authors'])>3 else ''}")
        print(f"  Keywords: {', '.join(p['keywords'][:5])}")
        print(f"  Abstract: {p.get('abstract', '')[:250]}...")
    
    # Save
    with open("papers/arxiv_filtered_2026-08-07.json", "w", encoding="utf-8") as f:
        json.dump({"date": "2026-08-07", "count": len(final), "papers": final}, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to papers/arxiv_filtered_2026-08-07.json")

if __name__ == "__main__":
    main()
