#!/usr/bin/env python3
"""Resumable arXiv fetcher v2: single-term queries, sorted by submittedDate
descending, paginate until entries fall below 2026-06-20, save raw pages.
Client-side filtering happens later. Run repeatedly until ALL DONE.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

OUT = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw"
STATE = os.path.join(OUT, "state2.json")
os.makedirs(OUT, exist_ok=True)

KEYWORDS = [
    "quantization", "pruning", "sparsity", "distillation",
    '"knowledge distillation"', '"KV cache"', '"mixed precision"',
    "GPTQ", "AWQ", '"low-bit"', '"model compression"',
    '"weight compression"', '"low precision"', '"post-training quantization"',
    '"model pruning"', '"vector quantization"', "quantize", "quantized",
    '"sparse training"', '"KV cache compression"',
]
STOP_DATE = "2026-06-20"  # stop paginating when oldest entry on page is older
SLEEP = 15.0
MAX_REQ = int(sys.argv[1]) if len(sys.argv) > 1 else 10
MAX_PAGES = 12  # safety cap per keyword


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"pages": {}}


def save_state(s):
    json.dump(s, open(STATE, "w"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace"), 200
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            print(f"  HTTP {e.code}, wait 45s", flush=True)
            time.sleep(45)
        except Exception as e:
            print(f"  err {e}, wait 45s", flush=True)
            time.sleep(45)
    return None, None


def oldest_date(xml):
    ds = re.findall(r"<published>(\d{4}-\d{2}-\d{2})", xml)
    return min(ds) if ds else "9999"


def main():
    state = load_state()
    reqs = 0
    for kw in KEYWORDS:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", kw).strip("_")
        for p in range(MAX_PAGES):
            tag = f"{slug}#p{p}"
            if tag in state["pages"]:
                if state["pages"][tag] == "STOP":
                    break
                continue
            if reqs >= MAX_REQ:
                save_state(state)
                print(f"PAUSED after {reqs} requests")
                return
            q = urllib.parse.quote(f"all:{kw}")
            url = (f"https://export.arxiv.org/api/query?search_query={q}"
                   f"&start={p*100}&max_results=100&sortBy=submittedDate&sortOrder=descending")
            xml, code = fetch(url)
            reqs += 1
            if xml is None:
                save_state(state)
                print("FETCH FAILED, rerun later")
                return
            fn = os.path.join(OUT, f"v2_{slug}_p{p}.xml")
            open(fn, "w").write(xml)
            od = oldest_date(xml)
            n = xml.count("<entry>")
            print(f"{kw} p{p}: {n} entries, oldest={od}", flush=True)
            if od < STOP_DATE or n == 0:
                state["pages"][tag] = "STOP"
                save_state(state)
                break
            state["pages"][tag] = "ok"
            save_state(state)
            time.sleep(SLEEP)
    save_state(state)
    print("ALL DONE")


if __name__ == "__main__":
    main()
