#!/usr/bin/env python3
"""ArXiv daily paper collector for model compression."""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import json
import os
import sys
from datetime import datetime, timedelta

def fetch_arxiv(keywords, target_date, categories=["cs.LG", "cs.CL", "cs.CV"], max_results=200):
    """Fetch papers from arXiv API with keyword filtering."""
    
    # Build keyword query
    kw_parts = []
    for kw in keywords:
        kw_parts.append(f'all:"{kw}"')
    keyword_query = " OR ".join(kw_parts)
    
    # Category filter
    cat_filter = " OR ".join(f"cat:{c}" for c in categories)
    
    # Full query
    query = f"({keyword_query}) AND ({cat_filter})"
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    print(f"Fetching: {url[:150]}...")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (reading-machine/1.0)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8")
        return data
    except Exception as e:
        print(f"ERROR fetching arXiv: {e}")
        return None

def parse_feed(xml_text, target_date):
    """Parse arXiv Atom feed and filter by date."""
    papers = []
    
    # arXiv uses Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"XML parse error: {e}")
        print(xml_text[:500])
        return papers
    
    for entry in root.findall("atom:entry", ns):
        # Title
        title_elem = entry.find("atom:title", ns)
        title = title_elem.text.strip() if title_elem is not None else ""
        
        # Summary (abstract)
        summary_elem = entry.find("atom:summary", ns)
        abstract = summary_elem.text.strip() if summary_elem is not None else ""
        
        # ID -> arxiv_id
        id_elem = entry.find("atom:id", ns)
        arxiv_id = ""
        if id_elem is not None:
            m = re.search(r'arxiv\.org/abs/(.+)', id_elem.text)
            if m:
                arxiv_id = m.group(1)
        
        # Published date
        published_elem = entry.find("atom:published", ns)
        pub_date = published_elem.text[:10] if published_elem is not None else ""
        
        # Updated date
        updated_elem = entry.find("atom:updated", ns)
        updated_date = updated_elem.text[:10] if updated_elem is not None else ""
        
        # Filter by target date (check both published and updated)
        if pub_date != target_date and updated_date != target_date:
            continue
        
        # Authors
        authors = []
        for author in entry.findall("atom:author", ns):
            name_elem = author.find("atom:name", ns)
            if name_elem is not None:
                authors.append(name_elem.text)
        
        # Categories
        categories = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term", "")
            if term:
                categories.append(term)
        
        # Primary category
        prim_cat = entry.find("arxiv:primary_category", ns)
        primary_category = prim_cat.get("term", "") if prim_cat is not None else ""
        
        paper = {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "published": pub_date,
            "updated": updated_date,
            "categories": categories,
            "primary_category": primary_category,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        }
        papers.append(paper)
    
    return papers

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    keywords = [
        "quantization", "quantize", "quantized", "low-bit",
        "model compression", "compress", "compressed",
        "pruning", "sparsity", "sparse",
        "knowledge distillation", "distillation",
        "KV cache compression", "KV cache",
        "mixed precision",
        "GPTQ", "AWQ", "GGUF",
        "INT4", "INT8", "FP4", "FP8", "NF4",
        "post-training quantization", "PTQ",
        "quantization-aware training", "QAT",
        "weight quantization", "activation quantization",
        "block quantization", "group-wise",
    ]
    
    print(f"=== ArXiv Daily Collector ===")
    print(f"Target date: {target_date}")
    print(f"Keywords: {len(keywords)} keyword groups")
    
    xml_data = fetch_arxiv(keywords, target_date)
    if xml_data is None:
        print("Failed to fetch from arXiv.")
        sys.exit(1)
    
    papers = parse_feed(xml_data, target_date)
    
    print(f"\n=== Results ===")
    print(f"Total papers matching date {target_date}: {len(papers)}")
    
    for p in papers:
        print(f"\n[{p['arxiv_id']}] {p['title']}")
        print(f"  Authors: {', '.join(p['authors'][:3])}{'...' if len(p['authors']) > 3 else ''}")
        print(f"  Categories: {', '.join(p['categories'])}")
        print(f"  Abstract: {p['abstract'][:200]}...")
    
    # Save results
    os.makedirs("papers", exist_ok=True)
    output_file = f"papers/arxiv_raw_{target_date}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"date": target_date, "count": len(papers), "papers": papers}, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_file}")

if __name__ == "__main__":
    main()
