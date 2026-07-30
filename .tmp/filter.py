import json, re
papers = json.load(open('harvest_relevant.json'))

def score(p):
    ti = p['title'].lower()
    ab = p['summary'].lower()
    s = 0
    hits = []
    def T(pat, w, tag):
        nonlocal s
        if re.search(pat, ti): s += w; hits.append(tag)
    def A(pat, w, tag):
        nonlocal s
        if re.search(pat, ab): s += w; hits.append(tag)
    # strong title signals: core compression methods
    T(r'quantiz', 4, 't-quant'); A(r'quantiz', 1, 'a-quant')
    T(r'prun', 4, 't-prune'); A(r'prun', 1, 'a-prune')
    T(r'distill', 3, 't-distill'); A(r'distill', 1, 'a-distill')
    T(r'spars', 2, 't-sparse')
    T(r'low[- ]?bit|few[- ]?bit|\b[1248][- ]?bit\b|bitwidth|binary|ternar|1\.58', 4, 't-lowbit')
    A(r'low[- ]?bit|\b[1248][- ]?bit\b|bitwidth', 1, 'a-lowbit')
    T(r'kv[- ]?cache|kv cache', 4, 't-kv')
    T(r'mixed[- ]precision', 3, 't-mixprec')
    T(r'compress', 3, 't-compress'); A(r'compress', 0.5, 'a-compress')
    T(r'fp4|fp8|int2|int4|int8|mxfp|nvfp|w4a4|w8a8|gptq|awq|smoothquant', 4, 't-fmt')
    A(r'fp4|int4|mxfp|nvfp|gptq|awq', 1, 'a-fmt')
    T(r'vq|vector quant|codebook|residual quant|semantic id', 2, 't-vq')
    T(r'on[- ]device|edge deploy|efficient inference|deploy', 1, 't-deploy')
    # target: neural models
    model_ctx = re.search(r'llm|large language|transformer|neural|cnn|diffusion|vision[- ]language|vlm|moe\b|bert|gpt|deep (neural|learning)|network', ti + ' ' + ab)
    if model_ctx: s += 1; hits.append('nn-ctx')
    # negative signals (off-topic contexts)
    neg = 0
    for pat, tag in [
        (r'quantile|quantum|tomography|holograph|black hole|lattice gauge', 'x-sci'),
        (r'\bcodec\b.*(video|audio|speech)|video codec|image codec', 'x-codec'),
        (r'tokeniz', 'x-tokenizer'),
        (r'sparse (matrix|solver|observation|regression|coding)|iterative hard thresholding', 'x-num'),
        (r'layout synthesis|analog circuit', 'x-eda'),
        (r'\brag\b|retrieval[- ]augmented|agent', 'x-rag'),
        (r'reinforcement learning|\brl\b', 'x-rl'),
        (r'dataset|benchmark(?!.*(quant|prun|compress|distill))', 'x-data'),
        (r'semantic communication|channel', 'x-semcom'),
    ]:
        if re.search(pat, ti): neg += 3; hits.append(tag)
    s -= neg
    return s, hits

rows = []
for k, p in papers.items():
    s, hits = score(p)
    rows.append((s, k, p['title'], hits))
rows.sort(reverse=True)
from collections import Counter
c = Counter()
for s, k, t, h in rows:
    c[round(s)] += 1
print(sorted(c.items()))
json.dump([{"score": s, "id": k, "title": t, "hits": h} for s, k, t, h in rows], open('scored.json','w'), ensure_ascii=False, indent=1)
