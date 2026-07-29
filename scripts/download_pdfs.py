#!/usr/bin/env python3
"""Download arXiv PDFs for daily collection."""

import json
import subprocess
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PAPERS_JSON = Path(__file__).parent.parent / "metadata" / "2026-07" / "papers_index.json"
PAPERS_DIR = Path(__file__).parent.parent / "papers" / "2026-07"

def download_paper(paper):
    arxiv_id = paper["id"]
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    paper_dir = PAPERS_DIR / arxiv_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = paper_dir / "paper.pdf"
    
    if pdf_path.exists() and pdf_path.stat().st_size > 10000:
        print(f"[SKIP] {arxiv_id} already downloaded ({pdf_path.stat().st_size} bytes)")
        return arxiv_id, "skipped"
    
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "60", "-o", str(pdf_path), pdf_url],
            capture_output=True, text=True, timeout=70
        )
        if pdf_path.exists() and pdf_path.stat().st_size > 10000:
            print(f"[OK] {arxiv_id} downloaded ({pdf_path.stat().st_size} bytes)")
            return arxiv_id, "ok"
        else:
            print(f"[FAIL] {arxiv_id} download failed or too small")
            if pdf_path.exists():
                pdf_path.unlink()
            return arxiv_id, "fail"
    except Exception as e:
        print(f"[ERROR] {arxiv_id}: {e}")
        return arxiv_id, "error"

def main():
    with open(PAPERS_JSON) as f:
        data = json.load(f)
    
    papers = data["papers"]
    print(f"Total papers to download: {len(papers)}")
    
    results = {"ok": 0, "skipped": 0, "fail": 0, "error": 0}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_paper, p): p for p in papers}
        for future in as_completed(futures):
            arxiv_id, status = future.result()
            results[status] += 1
    
    print(f"\n--- Summary ---")
    for k, v in results.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
