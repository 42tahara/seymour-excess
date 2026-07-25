"""dist2core regression (P0 green condition 1, SLOW ~5-10 min):

The rebuilt base model must reproduce the T2 lower-bound proof:
M_{17,2} (n=17, min_out=8, no digons, Seymour excess <= 2) is INFEASIBLE.

Run: python3 lib/dist2core/tests/test_n17_infeasible.py   (from repo root)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, ROOT)

import ortools                                               # noqa: E402
from ortools.sat.python import cp_model                      # noqa: E402
from lib.dist2core import build_base_model, add_seymour_excess  # noqa: E402


def test_n17_cap2_infeasible(workers=8, time_limit=3600.0):
    n, cap = 17, 2
    m, vars_ = build_base_model(n, allow_digons=False, min_out=8,
                                symmetry=True)
    add_seymour_excess(m, vars_, n, cap)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    t0 = time.time()
    status = solver.Solve(m)
    dt = time.time() - t0
    name = solver.StatusName(status)
    print(f"n={n} cap={cap}: {name} in {dt:.0f}s ({workers} workers)")
    # record artifact in the same style as data/sullivan/frontier.jsonl
    rec = {"n": n, "cap": cap, "status": name,
           "wall_time_seconds": round(dt, 1),
           "ortools_version": ortools.__version__,
           "random_seed": 1, "num_search_workers": workers,
           "model": "lib.dist2core.build_base_model + add_seymour_excess"}
    out = os.path.join(ROOT, "data", "t2_reprove_dist2core.json")
    with open(out, "w") as f:
        json.dump(rec, f, indent=2)
    print(f"record written: {out}")
    assert name == "INFEASIBLE", f"expected INFEASIBLE, got {name}"
    print("[PASS] rebuilt model reproduces E_{delta>=8}(17) >= 3")


if __name__ == "__main__":
    test_n17_cap2_infeasible()
