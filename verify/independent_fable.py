#!/usr/bin/env python3
# independent_verify_ca40b396.py — written by Fable from definitions only.
# No reference to repo verify.py. Pure stdlib.
import json, hashlib, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/champion_n53_ca40b396.json"
raw = json.load(open(PATH))
adj = raw["adj"] if "adj" in raw else raw
out = {int(v): sorted(set(int(w) for w in ws)) for v, ws in adj.items()}
n = len(out)
V = sorted(out)
assert V == list(range(n)), "vertex labels not 0..n-1"

# structural checks
self_loops = [v for v in V if v in out[v]]
digons = [(v, w) for v in V for w in out[v] if v in out[w] and v < w]
outdeg = {v: len(out[v]) for v in V}

# strong connectivity (BFS both directions from 0)
def reach(start, g):
    seen = {start}; stack = [start]
    while stack:
        u = stack.pop()
        for w in g[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return seen
rev = {v: [] for v in V}
for v in V:
    for w in out[v]:
        rev[w].append(v)
strong = (len(reach(0, out)) == n) and (len(reach(0, rev)) == n)

# margins: N2 = reachable in exactly two steps (excl. N1 and self)
margins = {}
for v in V:
    n1 = set(out[v])
    n2 = set()
    for u in n1:
        n2.update(out[u])
    n2 -= n1
    n2.discard(v)
    margins[v] = len(n2) - len(n1)

survivors = sorted(v for v in V if margins[v] >= 0)
excess = sum(max(0, d + 1) for d in margins.values())
hist = {}
for d in margins.values():
    hist[d] = hist.get(d, 0) + 1

# canonical hash (Fable recipe: sorted keys, sorted lists, compact JSON)
canon = json.dumps({str(v): out[v] for v in V},
                   sort_keys=True, separators=(",", ":"))
fable_sha1 = hashlib.sha1(canon.encode()).hexdigest()

print(f"n={n} arcs={sum(outdeg.values())} self_loops={self_loops} digons={len(digons)}")
print(f"outdeg min={min(outdeg.values())} max={max(outdeg.values())} strongly_connected={strong}")
print(f"excess={excess}")
print(f"survivors (margin>=0): {[(v, margins[v]) for v in survivors]}")
print(f"margin histogram: {dict(sorted(hist.items()))}")
print(f"fable_canonical_sha1={fable_sha1}")
print("EXPECT: digons=0, strong=True, min outdeg>=8,")
print("        excess=5, survivors=[(18,+1),(34,0),(35,0),(36,0)], all others negative")
