"""dist2core regression tests (P0 green conditions 2 & 3):

  2. Known witnesses reproduce their excess values, 3 implementations agreeing.
  3. pure-ring n=24 (m=3, t=8) reproduces all theory values:
     margins (pure m=0, impure m=-1), alpha in {0, 8} with counts {0:192, 8:21},
     tt = 336, exc = 3.

Run: python3 lib/dist2core/tests/test_regression.py   (from repo root)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data")

from lib.dist2core import (                                  # noqa: E402
    adj_from_dict, cross_check,
    d1_np, d2_np, o_np, tt_np, exc_np,
)

WITNESS_EXPECTED_EXC = {
    "champion_28da4a1e.json": 5,       # n=50, graph 17cd7dc8
    "champion_n53_ca40b396.json": 5,   # n=53, graph dc922e89
    "champion_n47_a76a5072.json": 9,
    "champion_n49_ad5efc8b.json": 6,
    "champion_n59_24dc568c.json": 7,
    "champion_d74d6509.json": 8,       # n=50, earlier witness
}


def test_witness_excess():
    for fname, expected in WITNESS_EXPECTED_EXC.items():
        w = json.load(open(os.path.join(DATA, fname)))
        adj = w["adj"] if isinstance(w, dict) and "adj" in w else w
        A = adj_from_dict(adj, len(adj))
        res = cross_check(A)                        # 3-impl agreement
        assert res["exc"] == expected, (fname, res["exc"], expected)
        print(f"[PASS] {fname}: exc = {expected} (3 implementations agree)")


def test_pure_ring_theory():
    A = json.load(open(os.path.join(DATA, "pure_ring_n24_m3.json")))
    n, t = 24, 8
    res = cross_check(A)
    d1 = res["d1"]
    d2 = res["d2"]
    m = [d2[v] - d1[v] for v in range(n)]

    # margins: pure vertices (one per layer) m=0, impure m=-1
    pures = [v for v in range(n) if m[v] == 0]
    impures = [v for v in range(n) if m[v] == -1]
    assert len(pures) == 3 and len(impures) == 21, (pures, impures)

    # excess = 3 (one per pure vertex)
    assert res["exc"] == 3, res["exc"]

    # tt = 336
    assert res["tt"] == 336, res["tt"]

    # alpha(u,v) = d2(u) - d1(v) + o(u,v) on arcs: values exactly {0: 192, 8: 21}
    o = res["o"]
    from collections import Counter
    alpha_counts = Counter(d2[u] - d1[v] + ov for (u, v), ov in o.items())
    assert dict(alpha_counts) == {0: 192, 8: 21}, dict(alpha_counts)
    print("[PASS] pure-ring n=24: margins, exc=3, tt=336, alpha in {0:192, 8:21}")


if __name__ == "__main__":
    test_witness_excess()
    test_pure_ring_theory()
    print("ALL GREEN")
