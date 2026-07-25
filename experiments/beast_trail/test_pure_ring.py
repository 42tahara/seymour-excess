"""Part A-4: pure-ring (n=24, m=3, t=8) sanity test.

Verifies:
  1. numpy and pure-python arc-alpha implementations agree on every arc
  2. For each forward inter-layer arc u->v, alpha(u,v) is what theory predicts:
     - all cross-layer forward arcs are tight (alpha=0) — this is stronger than
       the initial claim 'only impure->impure'; we verify the actual pattern
       and record it
  3. Intra-layer impure->pure arcs have alpha equal to d1(impure) - d1(pure) + (t-1)
     (which is o(impure, pure) contribution)
  4. The excess bound from the arc-inequality on a cross-layer 3-cycle
     recovers the well-known 'E <= k' construction
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))

from slack_lib import (
    pure_ring, compute_alpha_np, compute_alpha_pp,
    compute_basic_np, cross_check, is_pure,
)


def test_pure_ring_24():
    k, t = 3, 8
    A = pure_ring(k, t)
    N = k * t
    assert N == 24

    # (1) both implementations agree
    assert cross_check(A)

    # basic quantities
    basic = compute_basic_np(A)
    d1, d2, m = basic["d1"], basic["d2"], basic["m"]

    # pure vertices: d1 = t, d2 = t, m = 0
    # impure vertices: d1 = t+1 (one intra-layer to pure), d2 = t, m = -1
    for v in range(N):
        if is_pure(v, t):
            assert int(d1[v]) == t, f"pure {v} d1={d1[v]}"
            assert int(m[v]) == 0, f"pure {v} m={m[v]}"
        else:
            assert int(d1[v]) == t + 1, f"impure {v} d1={d1[v]}"
            assert int(m[v]) == -1, f"impure {v} m={m[v]}"

    alphas, _ = compute_alpha_np(A)

    tight_arcs = [(u, v) for (u, v), (a, _) in alphas.items() if a == 0]
    nontight = [(u, v, a) for (u, v), (a, _) in alphas.items() if a != 0]

    # (2) classify tight arcs by (block of u, block of v, pure/impure of u, of v)
    def blk(x):
        return x // t
    counts = {"pp_cross": 0, "pi_cross": 0, "ip_cross": 0, "ii_cross": 0,
              "impure_to_pure_intra": 0, "other": 0}
    for u, v in tight_arcs:
        bu, bv = blk(u), blk(v)
        pu, pv = is_pure(u, t), is_pure(v, t)
        if bu != bv:  # cross-layer
            key = ("p" if pu else "i") + ("p" if pv else "i") + "_cross"
            counts[key] += 1
        elif not pu and pv:
            counts["impure_to_pure_intra"] += 1
        else:
            counts["other"] += 1

    # All cross-layer forward arcs should be tight.
    # Cross-layer counts per (kind of u, kind of v):
    #  pp: 1 pure per layer -> 1 pure of next: k arcs
    #  pi: 1 pure -> (t-1) impure: k*(t-1) arcs
    #  ip: (t-1) impure -> 1 pure: k*(t-1) arcs
    #  ii: (t-1) impure -> (t-1) impure: k*(t-1)^2 arcs
    assert counts["pp_cross"] == k, counts
    assert counts["pi_cross"] == k * (t - 1), counts
    assert counts["ip_cross"] == k * (t - 1), counts
    assert counts["ii_cross"] == k * (t - 1) ** 2, counts

    # No intra-layer tight arcs (impure->pure intra has alpha = t-1)
    assert counts["impure_to_pure_intra"] == 0, counts
    assert counts["other"] == 0, counts

    # (3) intra-layer impure->pure arcs
    for u in range(N):
        if is_pure(u, t):
            continue
        pure_of_layer = (u // t) * t
        # arc u -> pure_of_layer
        a, o = alphas[(u, pure_of_layer)]
        # d1(impure)=t+1, d1(pure)=t, m(impure)=-1, o = |{pure_of_layer, next_layer} & next_layer|
        # = t (all of next layer). So alpha = -1 + (t+1) - t + t = t.
        assert a == t, f"intra impure->pure alpha={a}, expected {t}"

    # (4) telescoping check on a cross-layer 3-cycle (pure of layer 0 -> pure 1 -> pure 2 -> pure 0)
    cyc = [0 * t, 1 * t, 2 * t]
    m_sum = sum(int(m[v]) for v in cyc)  # 0
    o_sum = 0
    for i, u in enumerate(cyc):
        v = cyc[(i + 1) % k]
        _, o = alphas[(u, v)]
        o_sum += o
    # Sum of alpha on cycle = m_sum + o_sum (telescope kills d1) and should be 0 (all tight).
    assert m_sum + o_sum == 0, (m_sum, o_sum)

    return {
        "N": N, "k": k, "t": t,
        "tight_arc_count": len(tight_arcs),
        "nontight_arc_count": len(nontight),
        "cross_layer_tight_breakdown": {
            "pure->pure": counts["pp_cross"],
            "pure->impure": counts["pi_cross"],
            "impure->pure": counts["ip_cross"],
            "impure->impure": counts["ii_cross"],
        },
        "intra_impure_to_pure_alpha": t,
        "note": ("All cross-layer forward arcs are tight (alpha=0), not just "
                 "impure->impure. Intra-layer impure->pure has alpha=t."),
    }


if __name__ == "__main__":
    res = test_pure_ring_24()
    print("PASS")
    print(json.dumps(res, indent=2))
