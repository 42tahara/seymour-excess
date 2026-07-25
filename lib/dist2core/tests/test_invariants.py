"""dist2core fast tests: 3-implementation agreement + QK oracle basics.

Run: python3 lib/dist2core/tests/test_invariants.py   (from repo root)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".."))

from lib.dist2core import (                                  # noqa: E402
    cross_check, qk_check_np, qk_check_pp, qk_check_sd,
    qk_min, qk_min_brute,
)


def random_oriented(n, p, rng):
    A = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(i + 1, n):
            r = rng.random()
            if r < p / 2:
                A[i, j] = 1
            elif r < p:
                A[j, i] = 1
    return A


def random_digraph(n, p, rng):
    """digons allowed, loops not"""
    A = (rng.random((n, n)) < p).astype(np.int8)
    np.fill_diagonal(A, 0)
    return A


def test_cross_check_random():
    rng = np.random.default_rng(2026)
    for trial in range(30):
        n = int(rng.integers(3, 14))
        p = float(rng.uniform(0.1, 0.9))
        A = random_oriented(n, p, rng)
        cross_check(A)
    for trial in range(30):
        n = int(rng.integers(3, 12))
        p = float(rng.uniform(0.1, 0.7))
        A = random_digraph(n, p, rng)
        cross_check(A)
    print("[PASS] cross_check on 30 oriented + 30 digon-allowed random graphs")


def test_qk_check_agreement():
    rng = np.random.default_rng(7)
    agree = 0
    for trial in range(200):
        n = int(rng.integers(3, 10))
        A = random_digraph(n, 0.4, rng)
        k = int(rng.integers(1, n + 1))
        Q = list(rng.choice(n, size=k, replace=False))
        r = (qk_check_np(A, Q), qk_check_pp(A, Q), qk_check_sd(A, Q))
        assert r[0] == r[1] == r[2], (A.tolist(), Q, r)
        agree += 1
    print(f"[PASS] qk_check 3-impl agreement on {agree} random (G, Q) pairs")


def test_qk_min_vs_brute():
    rng = np.random.default_rng(11)
    checked = 0
    for trial in range(40):
        n = int(rng.integers(3, 9))
        A = random_digraph(n, 0.35, rng)
        # ensure sink-free not required for qk_min correctness; test as-is
        k_ilp, Q_ilp, status = qk_min(A, time_limit=30)
        k_bf, _ = qk_min_brute(A)
        assert status == "OPTIMAL", status
        assert k_ilp == k_bf, (A.tolist(), k_ilp, k_bf)
        assert qk_check_sd(A, Q_ilp), "ILP returned a non-QK set"
        checked += 1
    print(f"[PASS] qk_min ILP == brute force on {checked} random digraphs")


def test_qk_chvatal_lovasz():
    """Every digraph has a quasi-kernel (Chvatal-Lovasz 1974): qk_min never None."""
    rng = np.random.default_rng(13)
    for trial in range(50):
        n = int(rng.integers(2, 9))
        A = random_digraph(n, 0.5, rng)
        k, Q, status = qk_min(A, time_limit=30)
        assert k is not None and status == "OPTIMAL", (A.tolist(), status)
    print("[PASS] Chvatal-Lovasz sanity: QK always exists (50 digraphs)")


if __name__ == "__main__":
    test_cross_check_random()
    test_qk_check_agreement()
    test_qk_min_vs_brute()
    test_qk_chvatal_lovasz()
    print("ALL GREEN")
