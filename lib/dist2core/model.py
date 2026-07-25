"""CP-SAT base model with distance-2 variables, extracted from
experiments/delta8/excess2_search.py.

Constraint labels (used in the note's Appendix A and throughout docs):
  (O)  orientation:  a_ij + a_ji <= 1 for i < j    (omitted if allow_digons)
  (S1) s_vw + a_vw <= 1                            (N++ excludes N+)
  (S2) BoolOr(!a_vy, !a_yw, a_vw, s_vw)            (2-path forces s_vw = 1)
  (B)  symmetry breaking: vertex 0 has maximum out-degree and its
       out-neighbourhood is the initial segment {1..d0}

Soundness (same argument as excess2_search): s_vw is FORCED to 1 whenever a
2-path v->y->w exists and no direct arc v->w does; spurious 1s are possible
assignments but never forced. Hence sum_w s_vw >= d2(v) in every feasible
assignment, so any excess-style constraint written with s over-counts and
INFEASIBLE verdicts are sound. FEASIBLE outputs must still be re-verified
exactly (lib.dist2core.invariants) before being believed.

Note (B) is a relabeling symmetry and stays valid with digons and with
in-degree bounds; it is on by default and can be disabled.
"""
from ortools.sat.python import cp_model


def build_base_model(n, allow_digons=False, min_out=None, min_in=None,
                     symmetry=True):
    """Return (model, vars) where vars is a dict with:
       arc  : {(i,j): BoolVar}   i != j
       sec  : {(v,w): BoolVar}   v != w    (distance-2 indicator, >= semantics)
       out  : [LinearExpr] * n   out-degree expressions
       inn  : [LinearExpr] * n   in-degree expressions
    """
    m = cp_model.CpModel()
    arc = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                arc[(i, j)] = m.NewBoolVar(f"a{i}_{j}")

    if not allow_digons:                                    # (O)
        for i in range(n):
            for j in range(i + 1, n):
                m.Add(arc[(i, j)] + arc[(j, i)] <= 1)

    out = [sum(arc[(i, j)] for j in range(n) if j != i) for i in range(n)]
    inn = [sum(arc[(i, j)] for i in range(n) if i != j) for j in range(n)]

    if min_out is not None:
        for i in range(n):
            m.Add(out[i] >= min_out)
    if min_in is not None:
        for j in range(n):
            m.Add(inn[j] >= min_in)

    sec = {}
    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            sv = m.NewBoolVar(f"s{v}_{w}")
            sec[(v, w)] = sv
            m.Add(sv + arc[(v, w)] <= 1)                    # (S1)
            for y in range(n):
                if y in (v, w):
                    continue
                m.AddBoolOr([arc[(v, y)].Not(), arc[(y, w)].Not(),
                             arc[(v, w)], sv])              # (S2)

    if symmetry:                                            # (B)
        for i in range(1, n):
            m.Add(out[0] >= out[i])
        for j in range(1, n - 1):
            m.Add(arc[(0, j)] >= arc[(0, j + 1)])

    return m, {"arc": arc, "sec": sec, "out": out, "inn": inn}


def add_seymour_excess(m, vars_, n, cap):
    """exc(G) = sum_v max(0, d2(v) - d1(v) + 1) <= cap.  Returns ex vars."""
    sec, out = vars_["sec"], vars_["out"]
    ex = []
    for v in range(n):
        e = m.NewIntVar(0, n, f"ex{v}")
        m.Add(e >= sum(sec[(v, w)] for w in range(n) if w != v) - out[v] + 1)
        ex.append(e)
    m.Add(sum(ex) <= cap)
    return ex


def add_sullivan_excess(m, vars_, n, cap):
    """exc-(G) = sum_v max(0, d2(v) - d_minus(v) + 1) <= cap.  Returns ex vars.

    exc-(G) = 0  <=>  every vertex has d2(v) <= d_minus(v) - 1
              <=>  G has no Sullivan vertex (d2(v) >= d_minus(v))
              <=>  G is a counterexample to Sullivan's conjecture.
    """
    sec, inn = vars_["sec"], vars_["inn"]
    ex = []
    for v in range(n):
        e = m.NewIntVar(0, n, f"exm{v}")
        m.Add(e >= sum(sec[(v, w)] for w in range(n) if w != v) - inn[v] + 1)
        ex.append(e)
    m.Add(sum(ex) <= cap)
    return ex


def extract_adjacency(solver, vars_, n):
    """0/1 matrix from a solved model."""
    arc = vars_["arc"]
    return [[1 if i != j and solver.Value(arc[(i, j)]) else 0
             for j in range(n)] for i in range(n)]
