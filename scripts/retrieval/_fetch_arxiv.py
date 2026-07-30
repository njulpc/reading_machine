#!/usr/bin/env python3
"""Resumable arXiv API fetcher for 2026-07 model-compression papers.

Rate-limit friendly: sleeps between requests, persists raw XML pages,
resumable via state file. Run repeatedly until it prints ALL DONE.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

OUT = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw"
STATE = os.path.join(OUT, "state.json")
os.makedirs(OUT, exist_ok=True)

DATE_RANGE = "submittedDate:[202607010000+TO+202607292359]"
CATS = "(cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.AR+OR+cat:cs.IR+OR+cat:cs.CR+OR+cat:cs.IT+OR+cat:cs.DC+OR+cat:eess.AS+OR+cat:eess.SP+OR+cat:stat.ML)"
KEYWORDS = [
    "all:quantization", "all:quantize", "all:low-bit", "%22model+compression%22",
    "all:pruning", "all:sparsity", "%22knowledge+distillation%22",
    "%22KV+cache%22", "%22mixed+precision%22", "all:GPTQ", "all:AWQ",
    "%22weight+compression%22", "%22neural+network+compression%22",
    "%22model+pruning%22", "%22network+quantization%22", "all:distillation",
    "%22low+precision%22", "all:quantized", "%22post-training+quantization%22",
    "%22vector+quantization%22",
]
SLEEP = 12.0
MAX_REQ_PER_RUN = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"done": [], "totals": {}}


def save_state(s):
    json.dump(s, open(STATE, "w"), indent=1)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine-research/1.0 (mailto:research@example.com)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)
                print(f"  429 rate-limited, waiting {wait}s", flush=True)
                time.sleep(wait)
            else:
                print(f"  HTTP {e.code}, retry in 30s", flush=True)
                time.sleep(30)
        except Exception as e:
            print(f"  error {e}, retry in 30s", flush=True)
            time.sleep(30)
    return None


def main():
    state = load_state()
    reqs = 0
    for kw in KEYWORDS:
        q = f"{kw}+AND+{CATS}+AND+{DATE_RANGE}"
        base = f"https://export.arxiv.org/api/query?search_query={q}&sortBy=submittedDate&sortOrder=ascending"
        key = kw
        if key not in state["totals"]:
            if reqs >= MAX_REQ_PER_RUN:
                save_state(state); print(f"PAUSED after {reqs} requests"); return
            xml = fetch(base + "&start=0&max_results=100")
            reqs += 1
            if xml is None:
                save_state(state); print("FAILED, rerun later"); return
            m = re.search(r"<opensearch:totalResults[^>]*>(\d+)", xml)
            total = int(m.group(1)) if m else 0
            state["totals"][key] = total
            fn = os.path.join(OUT, f"q{KEYWORDS.index(kw):02d}_p0.xml")
            open(fn, "w").write(xml)
            print(f"{kw}: total={total} page0 saved", flush=True)
            time.sleep(SLEEP)
        total = state["totals"][key]
        npages = max(1, (total + 99) // 100)
        for p in range(1, npages):
            tag = f"{key}#p{p}"
            if tag in state["done"]:
                continue
            if reqs >= MAX_REQ_PER_RUN:
                save_state(state); print(f"PAUSED after {reqs} requests"); return
            xml = fetch(base + f"&start={p*100}&max_results=100")
            reqs += 1
            if xml is None:
                save_state(state); print("FAILED, rerun later"); return
            open(os.path.join(OUT, f"q{KEYWORDS.index(kw):02d}_p{p}.xml"), "w").write(xml)
            state["done"].append(tag)
            print(f"{kw}: page {p} saved", flush=True)
            time.sleep(SLEEP)
    save_state(state)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
