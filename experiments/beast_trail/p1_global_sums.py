"""P1: global-sum measurements + T/|E| ratio table.

For each witness (and pure-ring baseline), compute:
  E       = number of arcs
  T       = sum over arcs of o(u,v)          = number of transitive triangles
                                             (each triangle counted once,
                                              by its base arc)
  Sm      = sum_v m(v)                       (total Seymour deficit)
  Smd1    = sum_v m(v) * d1(v)
  Sd1imb  = sum_v d1(v) * (d+(v) - d-(v))    (imbalance term over WHOLE graph)
  T_over_E = T / E

Also emit the exact excess = sum_v max(0, m(v)+1) for context.

Global identity (all arcs, alpha>=0):
  sum_arcs alpha  =  Smd1  +  sum_u d1(u)^2  -  sum_v d-(v) d1(v)  +  T
                 =  Smd1  +  Sd1imb                                +  T
So  sum_arcs alpha  =  Smd1 + Sd1imb + T   should hold and be >= 0.

The user's claim: for exc<=1 counterexamples, T/|E| >= ~1 should be enforced.
We measure how far these near-witnesses (all exc>=5) sit from that boundary.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
import numpy as np
from slack_lib import adj_from_dict, compute_alpha_np, pure_ring


def sums_for(A: np.ndarray) -> dict:
    N = A.shape[0]
    alphas, basic = compute_alpha_np(A)
    d1 = basic["d1"].astype(int)
    d2 = basic["d2"].astype(int)
    m = basic["m"].astype(int)
    # in-degree
    dm = A.sum(axis=0).astype(int)

    E = int(A.sum())
    T = int(sum(o for _, o in alphas.values()))
    sum_alpha = int(sum(a for a, _ in alphas.values()))
    Sm = int(m.sum())
    Smd1 = int((m * d1).sum())
    Sd1_sq = int((d1 * d1).sum())
    Sd1_dm = int((d1 * dm).sum())
    Sd1imb = Sd1_sq - Sd1_dm  # = sum d1(v)*(d+(v)-d-(v))
    excess = int(np.maximum(0, m + 1).sum())
    min_out = int(d1.min())

    # sanity: sum_alpha == Smd1 + Sd1imb + T ?
    identity_check = Smd1 + Sd1imb + T - sum_alpha  # should be 0

    return {
        "N": N,
        "E": E,
        "T": T,
        "T_over_E": T / E,
        "Sm": Sm,
        "Smd1": Smd1,
        "Sd1imb": Sd1imb,
        "sum_alpha_over_arcs": sum_alpha,
        "identity_gap_should_be_zero": identity_check,
        "excess": excess,
        "min_out": min_out,
    }


def main():
    witnesses = [
        ("n24_pure_ring_k3t8", None),  # constructed
        ("n47_ad1a1ee5",       os.path.join(DATA, "champion_n47_a76a5072.json")),
        ("n49_ead3c3c3",       os.path.join(DATA, "champion_n49_ad5efc8b.json")),
        ("n50_17cd7dc8",       os.path.join(DATA, "champion_28da4a1e.json")),
        ("n53_dc922e89",       os.path.join(DATA, "champion_n53_ca40b396.json")),
        ("n59_c44e402b",       os.path.join(DATA, "champion_n59_24dc568c.json")),
    ]
    rows = []
    for lbl, path in witnesses:
        if path is None:
            A = pure_ring(3, 8)
        else:
            w = json.load(open(path))
            adj = w["adj"]
            N = int(w["N"]) if w.get("N") else len(adj)
            A = adj_from_dict(adj, N)
        r = sums_for(A)
        r["label"] = lbl
        rows.append(r)
    # emit table
    hdr = f"{'label':<24} {'N':>3} {'E':>5} {'exc':>4} {'T':>6} {'T/E':>7} {'Sm':>6} {'Smd1':>8} {'Sd1imb':>7} {'sumα':>7} {'gap':>4}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['label']:<24} {r['N']:>3} {r['E']:>5} {r['excess']:>4} "
              f"{r['T']:>6} {r['T_over_E']:>7.3f} {r['Sm']:>6} {r['Smd1']:>8} "
              f"{r['Sd1imb']:>7} {r['sum_alpha_over_arcs']:>7} "
              f"{r['identity_gap_should_be_zero']:>4}")
    out = os.path.join(os.path.dirname(__file__), "p1_global_sums.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=2, default=int)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
