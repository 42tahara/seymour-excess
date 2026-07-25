"""Part A-1..3: arc-slack anatomy of near-witness graphs.

Usage: python3 analyze_witness.py <witness.json> <label>
"""
import json, os, sys, hashlib
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from slack_lib import adj_from_dict, compute_alpha_np, cross_check


def analyze(witness_path: str, label: str):
    with open(witness_path) as f:
        w = json.load(f)
    adj = w["adj"]
    N = int(w["N"]) if w.get("N") else len(adj)
    A = adj_from_dict(adj, N)
    # oriented graph sanity
    assert np.diag(A).sum() == 0
    assert (A & A.T).sum() == 0, "digon found — arc-inequality assumes oriented graph"
    # cross-check
    cross_check(A)
    alphas, basic = compute_alpha_np(A)
    d1 = basic["d1"].tolist()
    d2 = basic["d2"].tolist()
    m = basic["m"].tolist()

    # (1) histogram of alpha over all arcs
    hist = Counter(a for a, _ in alphas.values())
    hist_sorted = sorted(hist.items())
    num_arcs = sum(hist.values())

    # (2) tight-arc subgraph structure
    tight = [(u, v) for (u, v), (a, _) in alphas.items() if a == 0]
    tight_out = defaultdict(list); tight_in = defaultdict(list)
    for u, v in tight:
        tight_out[u].append(v); tight_in[v].append(u)
    tight_vertices = sorted(set(u for u, _ in tight) | set(v for _, v in tight))
    # in-out degree in tight subgraph
    tight_degrees = {v: (len(tight_in.get(v, [])), len(tight_out.get(v, [])))
                     for v in tight_vertices}
    # SCC / cycle presence via Tarjan on tight subgraph
    def sccs(nodes, out_map):
        idx = {}; low = {}; stack = []; on_stack = set(); res = []
        counter = [0]
        def strong(v):
            idx[v] = low[v] = counter[0]; counter[0] += 1
            stack.append(v); on_stack.add(v)
            for w in out_map.get(v, []):
                if w not in idx:
                    strong(w); low[v] = min(low[v], low[w])
                elif w in on_stack:
                    low[v] = min(low[v], idx[w])
            if low[v] == idx[v]:
                comp = []
                while True:
                    w = stack.pop(); on_stack.discard(w); comp.append(w)
                    if w == v: break
                res.append(comp)
        # iterative to avoid recursion limit
        for v in nodes:
            if v not in idx:
                # iterative Tarjan
                work = [(v, iter(out_map.get(v, [])))]
                idx[v] = low[v] = counter[0]; counter[0] += 1
                stack.append(v); on_stack.add(v)
                while work:
                    node, it = work[-1]
                    try:
                        w = next(it)
                        if w not in idx:
                            idx[w] = low[w] = counter[0]; counter[0] += 1
                            stack.append(w); on_stack.add(w)
                            work.append((w, iter(out_map.get(w, []))))
                        elif w in on_stack:
                            low[node] = min(low[node], idx[w])
                    except StopIteration:
                        if low[node] == idx[node]:
                            comp = []
                            while True:
                                w = stack.pop(); on_stack.discard(w); comp.append(w)
                                if w == node: break
                            res.append(comp)
                        work.pop()
                        if work:
                            parent = work[-1][0]
                            low[parent] = min(low[parent], low[node])
        return res
    tight_sccs = sccs(tight_vertices, tight_out)
    nontriv_sccs = [c for c in tight_sccs if len(c) > 1]

    # keystone / cluster overlap: identify "deep deficit" vertices m <= -10
    deep = sorted([v for v in range(N) if m[v] <= -10])
    keystones = sorted([v for v in range(N) if m[v] >= 5])  # heuristic
    tight_touching_deep = [v for v in deep
                           if len(tight_in.get(v, [])) + len(tight_out.get(v, [])) > 0]

    # (3) for the deepest deficit vertex(es), in-arc breakdown
    if deep:
        # pick 3 deepest
        deep_sorted = sorted(deep, key=lambda x: m[x])
        deep_report = []
        for v in deep_sorted[:5]:
            in_arcs = [(u, v) for u in range(N) if A[u, v]]
            per_arc = []
            for u, _ in in_arcs:
                a, o = alphas[(u, v)]
                per_arc.append({"u": u, "m_u": m[u], "d1_u": d1[u], "d1_v": d1[v],
                                "o": o, "alpha": a})
            per_arc.sort(key=lambda r: r["alpha"])
            # aggregate: how much of the deficit is "paid" by which arcs
            # From arc-ineq: sum over in-arcs of alpha >= |in-arcs| * (something)
            # Not the right accounting; but we can look at cycle contribution:
            # for arc u->v, o(u,v) counts w such that u,v both -> w, i.e.
            # a triangle u->v with base and u->w & v->w. The 'transitive triangle
            # with base u->v' is exactly the o(u,v).
            # We record for each incoming arc the o and alpha so we can see
            # who's covering the deficit.
            deep_report.append({
                "v": v, "m_v": m[v], "d1_v": d1[v], "d2_v": d2[v],
                "in_degree": len(in_arcs),
                "sum_alpha_over_in_arcs": sum(r["alpha"] for r in per_arc),
                "sum_o_over_in_arcs": sum(r["o"] for r in per_arc),
                "tight_in_arcs": [r for r in per_arc if r["alpha"] == 0],
                "top5_lowest_alpha_in_arcs": per_arc[:5],
            })
    else:
        deep_report = []

    # emit
    out = {
        "witness_label": label,
        "witness_sha1": hashlib.sha1(open(witness_path, "rb").read()).hexdigest(),
        "N": N,
        "graph_sha1": w.get("graph_sha1"),
        "num_arcs": num_arcs,
        "excess_sum_max0_dp1": int(sum(max(0, mv + 1) for mv in m)),
        "min_out_degree": int(min(d1)),
        "alpha_histogram": [{"alpha": a, "count": c} for a, c in hist_sorted],
        "alpha_stats": {
            "min": int(min(hist)), "max": int(max(hist)),
            "mean": float(sum(a * c for a, c in hist.items()) / num_arcs),
        },
        "tight_arc_count": len(tight),
        "tight_vertices_count": len(tight_vertices),
        "tight_nontrivial_sccs": [sorted(c) for c in nontriv_sccs],
        "tight_scc_sizes": sorted([len(c) for c in tight_sccs], reverse=True)[:10],
        "deep_deficit_vertices_m_le_-10": deep,
        "keystones_m_ge_5": keystones,
        "deep_reports": deep_report,
        "note_tight_subgraph": ("A directed cycle in the tight subgraph is a "
                                "certificate: sum m + sum o = 0 exactly on that cycle."),
    }
    return out


if __name__ == "__main__":
    path, label = sys.argv[1], sys.argv[2]
    res = analyze(path, label)
    out_path = os.path.join(os.path.dirname(__file__), f"slack_{label}.json")
    with open(out_path, "w") as f:
        json.dump(res, f, indent=2, default=int)
    print(f"wrote {out_path}")
    # brief summary to stdout
    print(f"N={res['N']} graph_sha1={res['graph_sha1']} num_arcs={res['num_arcs']}")
    print(f"excess={res['excess_sum_max0_dp1']} min_out={res['min_out_degree']}")
    print(f"alpha stats: min={res['alpha_stats']['min']} max={res['alpha_stats']['max']} mean={res['alpha_stats']['mean']:.2f}")
    print(f"tight arcs: {res['tight_arc_count']}  tight vertices: {res['tight_vertices_count']}")
    print(f"tight non-trivial SCCs (>1 vert): {len(res['tight_nontrivial_sccs'])}, sizes={res['tight_scc_sizes']}")
    print(f"deep-deficit (m<=-10) verts: {len(res['deep_deficit_vertices_m_le_-10'])}")
    print(f"histogram head (10 smallest alphas):")
    for row in res['alpha_histogram'][:10]:
        print(f"  alpha={row['alpha']:4d}  count={row['count']}")
