#!/usr/bin/env python3
"""Fetch metadata (abstract, published, categories) for listing candidates via arXiv API id_list batches,
then merge with the API keyword pool and apply relevance scoring."""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import sys

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
BASE = "https://export.arxiv.org/api/query"


def fetch_ids(ids):
    params = {"id_list": ",".join(ids), "max_results": len(ids)}
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "reading-machine/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            wait = 30 * (attempt + 1)
            print(f"  retry {attempt}: {e}; sleep {wait}", file=sys.stderr)
            time.sleep(wait)
    return None


def parse(xml_text):
    root = ET.fromstring(xml_text)
    out = {}
    for e in root.findall("atom:entry", NS):
        aid = e.find("atom:id", NS).text.split("/abs/")[-1]
        base = aid.split("v")[0]
        title = " ".join(e.find("atom:title", NS).text.split())
        summary = " ".join(e.find("atom:summary", NS).text.split())
        published = e.find("atom:published", NS).text
        updated = e.find("atom:updated", NS).text
        cats = [c.get("term") for c in e.findall("atom:category", NS)]
        authors = [a.find("atom:name", NS).text for a in e.findall("atom:author", NS)]
        out[base] = {"id": base, "title": title, "summary": summary,
                     "published": published, "updated": updated,
                     "categories": cats, "authors": authors}
    return out


def main():
    listing = json.load(open("listing_candidates.json"))
    ids = [p["id"] for p in listing]
    meta = {}
    B = 150
    for i in range(0, len(ids), B):
        chunk = ids[i:i + B]
        xml = fetch_ids(chunk)
        if xml:
            meta.update(parse(xml))
        print(f"fetched {i + len(chunk)}/{len(ids)}, meta={len(meta)}")
        time.sleep(4)
    json.dump(meta, open("listing_meta.json", "w"), ensure_ascii=False)
    print("done", len(meta))


if __name__ == "__main__":
    main()
