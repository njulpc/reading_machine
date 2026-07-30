#!/usr/bin/env python3
"""Scrape arXiv monthly listing pages for Jan 2026 across relevant categories,
collect id/title/authors/subjects, and filter by compression-related title keywords."""
import json
import re
import time
import urllib.request
import sys

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) reading-machine/1.0"}

CATS = ["cs.LG", "cs.CL", "cs.CV", "cs.AI", "cs.NE", "cs.AR",
        "eess.AS", "cs.IR", "cs.CR", "stat.ML", "cs.ET", "eess.IV"]

ENTRY_RE = re.compile(
    r'<dt>.*?/abs/(\d{4}\.\d{4,5})".*?</dt>\s*<dd>(.*?)</dd>', re.S)
TITLE_RE = re.compile(
    r"<div class='list-title mathjax'><span class='descriptor'>Title:</span>\s*(.*?)\s*</div>", re.S)
AUTH_RE = re.compile(
    r"<div class='list-authors'>(.*?)</div>", re.S)
SUBJ_RE = re.compile(
    r"<div class='list-subjects'><span class='descriptor'>Subjects:</span>\s*(.*?)\s*</div>", re.S)
TAG_RE = re.compile(r"<[^>]+>")

# broad title-keyword filter (recall first)
KW = re.compile(
    r"quantiz|quantiz|low[- ]?bit|prun|spars|distill|compress|kv[ -]?cache|"
    r"mixed[- ]precision|gptq|awq|binariz|ternar|1[- ]bit|2[- ]bit|4[- ]bit|"
    r"int4|int8|fp4|fp8|low[- ]rank|lora|qlora|weight[- ]sharing|slim|"
    r"tiny|efficient|accelerat|edge|on[- ]device|lightweight|mobile|"
    r"knowledge transfer|model reduction|bitwidth|bit[- ]width|memory[- ]efficient",
    re.I)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            wait = 20 * (attempt + 1)
            print(f"  retry {attempt}: {e}; sleep {wait}", file=sys.stderr)
            time.sleep(wait)
    return None


def clean(s):
    return re.sub(r"\s+", " ", TAG_RE.sub("", s)).strip()


def main():
    pool = {}
    for cat in CATS:
        skip = 0
        while True:
            url = f"https://arxiv.org/list/{cat}/2026-01?skip={skip}&show=2000"
            html = fetch(url)
            if html is None:
                print(f"FAILED {url}", file=sys.stderr)
                break
            m = re.search(r"of ([0-9,]+)", html)
            total = int(m.group(1).replace(",", "")) if m else 0
            entries = ENTRY_RE.findall(html)
            for aid, dd in entries:
                tm = TITLE_RE.search(dd)
                sm = SUBJ_RE.search(dd)
                am = AUTH_RE.search(dd)
                title = clean(tm.group(1)) if tm else ""
                subjects = clean(sm.group(1)) if sm else ""
                authors = clean(am.group(1)) if am else ""
                if aid not in pool:
                    pool[aid] = {
                        "id": aid, "title": title, "authors": authors,
                        "subjects": subjects,
                        "title_hit": bool(KW.search(title)),
                        "subj_hit": bool(KW.search(subjects)),
                    }
            print(f"{cat} skip={skip} entries={len(entries)} total={total} pool={len(pool)}")
            skip += len(entries)
            if skip >= total or not entries:
                break
            time.sleep(2.5)
        time.sleep(2.5)

    out = sorted(pool.values(), key=lambda x: x["id"])
    with open("listing_pool.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    hits = [p for p in out if p["title_hit"] or p["subj_hit"]]
    with open("listing_candidates.json", "w", encoding="utf-8") as f:
        json.dump(hits, f, ensure_ascii=False, indent=2)
    print(f"\nTotal unique: {len(out)}; keyword hits: {len(hits)}")


if __name__ == "__main__":
    main()
