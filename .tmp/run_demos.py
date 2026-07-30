import os, subprocess, sys, json
ROOT = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-06/scripts/quantization"
LOG = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-06/.tmp/demo_results.json"
res = json.load(open(LOG)) if os.path.exists(LOG) else {}
ids = sorted(os.listdir(ROOT))
todo = [i for i in ids if res.get(i) != "PASS"]
print(f"total {len(ids)}, todo {len(todo)}")
for i in todo:
    p = os.path.join(ROOT, i, "demo.py")
    try:
        r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=90)
        if r.returncode == 0 and "Demo finished" in r.stdout:
            res[i] = "PASS"
        else:
            res[i] = "FAIL: " + (r.stderr.strip().splitlines() or ["?"])[-1][:150]
    except subprocess.TimeoutExpired:
        res[i] = "FAIL: timeout"
    json.dump(res, open(LOG, "w"), indent=1)
    print(i, res[i][:60], flush=True)
fails = {k:v for k,v in res.items() if v != "PASS"}
print(f"\nPASS {sum(1 for v in res.values() if v=='PASS')}/{len(res)}; fails: {len(fails)}")
