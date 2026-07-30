#!/usr/bin/env python3
"""Parse raw arXiv pages, dedupe, filter to 2026-07 model-compression papers."""
import glob, json, os, re, html

RAW = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw"
OUT = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-07/_arxiv_raw/parsed.json"

TARGET_CATS = {"cs.LG","cs.CL","cs.CV","cs.AI","cs.NE","cs.AR","cs.IR","cs.CR",
               "cs.IT","cs.DC","cs.SE","eess.AS","eess.SP","stat.ML","cs.MA","cs.SY","cs.ET"}

NN_HINT = re.compile(r"neural|network|transformer|LLM|language model|deep |model|CNN|RNN|ViT|diffusion|attention|GPT|BERT|encoder|decoder|inference|weight|activation|token", re.I)

NEG_HINT = re.compile(r"quantum|quantization of|gauge|gravity|black hole|field theory|lattice|QCD|hamiltonian|photon|plasma|molecule|chemical|protein|genomic|MRI|radar signal|image compression|video coding|codec|JPEG|H\.26|speech codec", re.I)

papers = {}
for fn in glob.glob(os.path.join(RAW, "v2_*.xml")) + glob.glob(os.path.join(RAW, "q*.xml")):
    xml = open(fn, encoding="utf-8", errors="replace").read()
    kw = os.path.basename(fn)
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        m = re.search(r"<id>http://arxiv.org/abs/([^<]+)</id>", e)
        if not m:
            continue
        aid_full = m.group(1)
        aid = re.sub(r"v\d+$", "", aid_full)
        title = html.unescape(re.search(r"<title>(.*?)</title>", e, re.S).group(1)).strip()
        title = re.sub(r"\s+", " ", title)
        summ = html.unescape(re.search(r"<summary>(.*?)</summary>", e, re.S).group(1)).strip()
        summ = re.sub(r"\s+", " ", summ)
        pub = re.search(r"<published>([^<]+)</published>", e).group(1)[:10]
        cats = sorted(set(re.findall(r'term="([^"]+)"', e)))
        authors = re.findall(r"<name>([^<]+)</name>", e)
        if aid in papers:
            papers[aid]["matched_by"].append(kw)
            continue
        papers[aid] = {
            "id": aid, "title": title, "abstract": summ, "published": pub,
            "categories": cats, "authors": authors, "matched_by": [kw],
        }

print("total unique:", len(papers))

# date filter
in_date = {k: v for k, v in papers.items() if "2026-07-01" <= v["published"] <= "2026-07-29"}
print("in date range 07-01..07-29:", len(in_date))

# id sanity: arxiv id YYMM should be 2607
bad_id = [k for k in in_date if not k.startswith("2607.")]
print("ids not starting 2607:", len(bad_id), bad_id[:10])

# category filter
in_cat = {k: v for k, v in in_date.items() if set(v["categories"]) & TARGET_CATS}
print("in target cats:", len(in_cat))

# relevance: drop obvious non-NN (quantum physics etc.)
rel = {}
for k, v in in_cat.items():
    text = v["title"] + " " + v["abstract"]
    if NEG_HINT.search(v["title"]) and not NN_HINT.search(v["title"]):
        continue
    rel[k] = v
print("after relevance filter:", len(rel))

json.dump(sorted(rel.values(), key=lambda x: x["published"]), open(OUT, "w"), indent=1, ensure_ascii=False)
print("saved", OUT)
