"""P0: recheck of the tight-SCC identity.

For any set A of arcs with alpha=0 on every arc:
    0 = sum_{(u,v) in A} alpha(u,v)
      = sum_{(u,v) in A} [ m(u) + d1(u) - d1(v) + o(u,v) ]
      = sum_u d+_A(u) m(u)                       (weighted-m term)
        + sum_u d1(u) * (d+_A(u) - d-_A(u))      (imbalance term)
        + sum_{arc in A} o(u,v)                  (o term)
where d+_A(u), d-_A(u) are the out/in degrees inside the arc set A.

Two consequences:

  (unit-sum, WRONG in general):
      sum_{v in V(A)} m(v)  +  sum_{arc in A} o(u,v)  == 0
      Only true when d+_A(u)=1 for every vertex (Hamiltonian cycle covering
      exactly V(A) once) AND d+_A(u) = d-_A(u) (Eulerian).

  (weighted, ALWAYS true):
      sum_u d+_A(u) m(u) + sum_u d1(u)(d+_A(u) - d-_A(u)) + sum_arc o = 0

We measure both.  We also report the in/out-degree profile of the tight SCC
subgraph and whether it is Eulerian, or admits a directed cycle cover.
"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
import numpy as np
from slack_lib import adj_from_dict, compute_alpha_np


def identity_report(witness_path: str, label: str):
    with open(witness_path) as f:
        w = json.load(f)
    adj = w["adj"]
    N = int(w["N"]) if w.get("N") else len(adj)
    A = adj_from_dict(adj, N)
    alphas, basic = compute_alpha_np(A)
    d1 = basic["d1"].astype(int)
    m = basic["m"].astype(int)

    # tight arcs and their subgraph
    tight = [(u, v) for (u, v), (a, _) in alphas.items() if a == 0]
    o_of = {(u, v): o for (u, v), (a, o) in alphas.items() if a == 0}
    tight_o_sum = sum(o_of.values())

    # in/out degrees on the tight subgraph
    dp = Counter(); dm = Counter()
    for u, v in tight:
        dp[u] += 1; dm[v] += 1
    tight_vertices = sorted(set(dp) | set(dm))
    # per-vertex balance
    imbalance = {v: dp[v] - dm[v] for v in tight_vertices}

    # non-trivial SCCs (from previous analyze report structure)
    # rebuild: run Tarjan on tight arcs
    out_map = {v: [] for v in range(N)}
    for u, v in tight:
        out_map[u].append(v)

    def sccs_iter(nodes, out_map):
        idx = {}; low = {}; stack = []; on_stack = set(); res = []
        counter = [0]
        for v0 in nodes:
            if v0 in idx: continue
            work = [(v0, iter(out_map.get(v0, [])))]
            idx[v0] = low[v0] = counter[0]; counter[0] += 1
            stack.append(v0); on_stack.add(v0)
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
                            wv = stack.pop(); on_stack.discard(wv); comp.append(wv)
                            if wv == node: break
                        res.append(comp)
                    work.pop()
                    if work:
                        parent = work[-1][0]
                        low[parent] = min(low[parent], low[node])
        return res

    sccs = sccs_iter(range(N), out_map)
    nontriv = sorted([sorted(c) for c in sccs if len(c) > 1], key=len, reverse=True)

    # per SCC identity check
    report = {"label": label, "N": N,
              "graph_sha1": w.get("graph_sha1"),
              "num_tight_arcs": len(tight),
              "num_nontriv_sccs": len(nontriv),
              "nontriv_scc_sizes": [len(c) for c in nontriv],
              "sccs": []}

    for comp in nontriv:
        Sv = set(comp)
        # arcs inside SCC
        A_in = [(u, v) for (u, v) in tight if u in Sv and v in Sv]
        # (1) unit-sum identity check
        sum_m_unit = int(sum(m[v] for v in comp))
        sum_o_scc = int(sum(o_of[(u, v)] for (u, v) in A_in))
        unit_identity = sum_m_unit + sum_o_scc
        # (2) weighted identity check
        dp_A = Counter(); dm_A = Counter()
        for u, v in A_in:
            dp_A[u] += 1; dm_A[v] += 1
        sum_m_weighted = int(sum(dp_A[u] * m[u] for u in comp))
        sum_d1_imbalance = int(sum(d1[u] * (dp_A[u] - dm_A[u]) for u in comp))
        sum_o_weighted = int(sum(o_of[(u, v)] for (u, v) in A_in))
        weighted_identity = sum_m_weighted + sum_d1_imbalance + sum_o_weighted
        # per-vertex out-in profile
        dp_dist = sorted(Counter(dp_A[v] for v in comp).items())
        dm_dist = sorted(Counter(dm_A[v] for v in comp).items())
        # Eulerian? every vertex dp==dm
        is_eulerian = all(dp_A[v] == dm_A[v] for v in comp)
        # each vertex dp=dm=1 => single Hamiltonian cycle covering all V(A)
        report["sccs"].append({
            "size": len(comp),
            "arcs_inside": len(A_in),
            "unit_sum_m_scc": sum_m_unit,
            "unit_sum_o_scc": sum_o_scc,
            "unit_identity_value": unit_identity,   # SHOULD be 0 only if Eulerian & every dp=1
            "weighted_sum_m": sum_m_weighted,
            "weighted_sum_d1_imbalance": sum_d1_imbalance,
            "weighted_sum_o": sum_o_weighted,
            "weighted_identity_value": weighted_identity,  # MUST be 0 (identity)
            "is_eulerian_on_tight_subgraph": is_eulerian,
            "d_plus_distribution": dp_dist,
            "d_minus_distribution": dm_dist,
        })

    # overall identity check (all tight arcs, ignoring SCC decomposition)
    dp_all = Counter(); dm_all = Counter()
    for u, v in tight:
        dp_all[u] += 1; dm_all[v] += 1
    V_all = set(v for v, _ in [(u, dp_all[u]) for u in range(N)] if dp_all[u] > 0) | \
            set(v for v in range(N) if dm_all[v] > 0)
    sum_m_unit_all = int(sum(m[v] for v in V_all))
    sum_o_all = int(sum(o_of.values()))
    sum_m_w_all = int(sum(dp_all[u] * m[u] for u in range(N)))
    sum_d1_imb_all = int(sum(d1[u] * (dp_all[u] - dm_all[u]) for u in range(N)))
    report["overall_tight_arcs"] = {
        "unit_identity_value": sum_m_unit_all + sum_o_all,
        "weighted_identity_value": sum_m_w_all + sum_d1_imb_all + sum_o_all,
        "V_tight_size": len(V_all),
    }
    return report


if __name__ == "__main__":
    witnesses = [
        ("n50_17cd7dc8", os.path.join(DATA, "champion_28da4a1e.json")),
        ("n53_ca40b396", os.path.join(DATA, "champion_n53_ca40b396.json")),
    ]
    all_reports = []
    for lbl, path in witnesses:
        r = identity_report(path, lbl)
        all_reports.append(r)
        print(f"\n===== {lbl} (N={r['N']}) =====")
        print(f"  #tight arcs = {r['num_tight_arcs']}, non-triv SCCs = {r['num_nontriv_sccs']}, sizes = {r['nontriv_scc_sizes']}")
        print(f"  overall (all tight arcs): unit-identity = {r['overall_tight_arcs']['unit_identity_value']} (may != 0)")
        print(f"                            weighted-identity = {r['overall_tight_arcs']['weighted_identity_value']} (must == 0)")
        for i, sc in enumerate(r["sccs"]):
            print(f"  SCC #{i} (size={sc['size']}, arcs={sc['arcs_inside']}):")
            print(f"    unit-sum-m = {sc['unit_sum_m_scc']}, unit-sum-o = {sc['unit_sum_o_scc']}")
            print(f"    -> unit identity value = {sc['unit_identity_value']}  (0 only if Eulerian+Hamil)")
            print(f"    weighted-sum-m = {sc['weighted_sum_m']}")
            print(f"    weighted-d1-imbalance = {sc['weighted_sum_d1_imbalance']}")
            print(f"    weighted-sum-o = {sc['weighted_sum_o']}")
            print(f"    -> weighted identity value = {sc['weighted_identity_value']}  (MUST be 0)")
            print(f"    Eulerian on tight-subgraph? {sc['is_eulerian_on_tight_subgraph']}")
            print(f"    d+ dist: {sc['d_plus_distribution']}")
            print(f"    d- dist: {sc['d_minus_distribution']}")

    out = os.path.join(os.path.dirname(__file__), "p0_identity_results.json")
    with open(out, "w") as f:
        json.dump(all_reports, f, indent=2, default=int)
    print(f"\nwrote {out}")
