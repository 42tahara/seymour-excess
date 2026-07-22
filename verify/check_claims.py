#!/usr/bin/env python3
"""One-command verification of every claim in the README, mapped 1:1 to the
claim labels there.  "Don't trust us — run this."

Each check re-derives the claimed numbers with the independent pure-Python
verifier (verify_ssnc), never with the pipeline that produced them.

Usage: python3 check_claims.py            # all fast checks (seconds)
       python3 check_claims.py t1 t1p     # subset
       python3 check_claims.py t2-full    # re-run the n=17 CP-SAT proof (~4 min)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")

sys.path.insert(0, HERE)
from verify_ssnc import to_matrix, verify           # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "constructions"))
from power_ring import build, unified_bound          # noqa: E402


def load(name):
    return verify(to_matrix(json.load(open(os.path.join(DATA, name)))))


def check_t1():
    """T1: pure m-ring gives excess = m with min out-degree = n/m."""
    for f, m in [("pure_ring_n27_m3.json", 3), ("pure_ring_n48_m3.json", 3),
                 ("pure_ring_n51_m3.json", 3)]:
        r = load(f)
        assert r["excess"] == m and r["min_out_degree"] >= 8 \
            and r["strongly_connected"], (f, r)
    for m, t in [(3, 8), (4, 8), (5, 8), (6, 8)]:    # fresh rebuilds, k=1
        r = verify(build(m, 1, t).tolist())
        assert r["excess"] == m and r["min_out_degree"] == t, (m, t, r)
    return "pure rings: data witnesses + fresh k=1 rebuilds all give excess=m"


def check_t1p():
    """T1': C_m^k power ring reaches the deserts (n=25, 35, 49)."""
    for f, e in [("gkz_ring_n25_m5k2.json", 5), ("gkz_ring_n35_m5k2.json", 5),
                 ("gkz_ring_n49_m7k2.json", 7)]:
        r = load(f)
        assert r["excess"] == e and r["min_out_degree"] >= 8 \
            and r["strongly_connected"] and r["positive_margin_vertices"] == 0, (f, r)
    for n, e in [(20, 5), (21, 7), (28, 7)]:          # fresh rebuilds
        m, k, t = unified_bound(n)
        r = verify(build(m, k, t).tolist())
        assert m == e and r["excess"] == m and r["min_out_degree"] >= 8, (n, r)
    return "power rings: E(25)<=5, E(35)<=5, E(49)<=7 + fresh rebuilds"


def check_o1():
    """O1: evolved champions — E(50) <= 8 (d74d6509) and <= 5 (28da4a1e)."""
    for f, e in [("champion_d74d6509.json", 8), ("champion_28da4a1e.json", 5)]:
        r = load(f)
        assert r["n"] == 50 and r["excess"] == e and r["min_out_degree"] >= 8 \
            and r["strongly_connected"], (f, r)
    return "champions: excess 8 (d74d6509) and 5 (28da4a1e), delta>=8, strong"


def check_t5():
    """T5: Pisa Conjecture 5.1 counterexamples (independent implementation)."""
    out = subprocess.run([sys.executable, os.path.join(HERE, "pisa_check.py")],
                         capture_output=True, text=True)
    assert out.returncode == 0 and "PASS" in out.stdout, out.stdout + out.stderr
    r = load("pisa_n7_witness.json")
    assert r["n"] == 7 and r["positive_margin_vertices"] == 0, r
    return "Pisa refutation: 3 counterexamples + n=7 witness confirmed"


def check_t2():
    """T2 (log check): recorded CP-SAT INFEASIBLE for excess<=2 at n=17."""
    recs = [json.loads(l) for l in
            open(os.path.join(DATA, "excess2_results.jsonl"))]
    hit = [r for r in recs if r["n"] == 17 and r["cap"] == 2
           and r["status"] == "INFEASIBLE"]
    assert hit, "no n=17 INFEASIBLE record"
    return (f"n=17 excess<=2 INFEASIBLE on record "
            f"({hit[0]['wall_time_seconds']:.0f}s); run 't2-full' to re-prove")


def check_t2_full():
    """T2 (full): re-run the n=17 CP-SAT proof from scratch (~4 min)."""
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "experiments", "delta8",
                                      "excess2_search.py"),
         "--n", "17", "--cap", "2", "--time-limit", "3600",
         "--out", os.devnull], capture_output=True, text=True)
    rec = json.loads(out.stdout.strip().splitlines()[-1])
    assert rec["status"] == "INFEASIBLE", rec
    return f"n=17 re-proved INFEASIBLE in {rec['wall_time_seconds']:.0f}s"


def check_t6():
    """T6 (log + fast rerun): GKZ Conj 8.2, k=3 — no counterexample n<=9
    re-proved live; larger n from the recorded scan."""
    for n in (7, 8, 9):
        out = subprocess.run(
            [sys.executable, os.path.join(ROOT, "experiments", "gkz_conj82.py"),
             "--n", str(n), "--time-limit", "600", "--out", os.devnull],
            capture_output=True, text=True)
        rec = json.loads(out.stdout.strip().splitlines()[-1])
        assert rec["status"] == "INFEASIBLE", rec
    recs = [json.loads(l) for l in
            open(os.path.join(DATA, "gkz82_results.jsonl"))]
    ns = sorted(r["n"] for r in recs if r["status"] == "INFEASIBLE")
    hyp = [json.loads(l) for l in
           open(os.path.join(DATA, "gkz82_hypcheck.jsonl"))]
    hyp_ns = sorted(r["n"] for r in hyp
                    if r["status"] in ("FEASIBLE", "OPTIMAL"))
    assert set(ns) <= set(hyp_ns), "INFEASIBLE n lacking hypothesis witness"
    return (f"n=7..9 re-proved live; recorded scan: no counterexample for "
            f"n in {ns[0]}..{ns[-1]} (hypothesis graphs exist at each n)")


def check_hashes():
    """Manifest integrity."""
    out = subprocess.run([sys.executable,
                          os.path.join(HERE, "check_hashes.py")],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    return out.stdout.strip().splitlines()[-1]


CHECKS = {"t1": check_t1, "t1p": check_t1p, "o1": check_o1, "t5": check_t5,
          "t2": check_t2, "t6": check_t6, "hashes": check_hashes,
          "t2-full": check_t2_full}
FAST = ["hashes", "t1", "t1p", "o1", "t5", "t2", "t6"]


def main():
    names = sys.argv[1:] or FAST
    failed = False
    for name in names:
        try:
            msg = CHECKS[name]()
            print(f"PASS {name}: {msg}")
        except Exception as e:                       # noqa: BLE001
            print(f"FAIL {name}: {e}")
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
