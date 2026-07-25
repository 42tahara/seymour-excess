"""dist2core — shared distance-2 encoding + invariant library.

Extracted from experiments/delta8/excess2_search.py (Seymour M_{n,c} model)
and generalized for three conjecture families:

  * Seymour SSNC        exc(G)  = sum_v max(0, d2(v) - d1(v) + 1)
  * Sullivan (2006)     exc-(G) = sum_v max(0, d2(v) - d_minus(v) + 1)
  * Small Quasi-Kernel  qk_min(G) vs floor(n/2)   (sink-free digraphs, digons OK)

Model side (CP-SAT): build_base_model + add_seymour_excess / add_sullivan_excess.
Invariant side: every invariant has 3 independent implementations
(numpy / pure-python / stdlib-from-definitions); cross_check() asserts agreement.
"""

from .model import (
    build_base_model,
    add_seymour_excess,
    add_sullivan_excess,
    extract_adjacency,
)
from .invariants import (
    d1_np, d1_pp, d1_sd,
    d2_np, d2_pp, d2_sd,
    d_minus_np, d_minus_pp, d_minus_sd,
    dpp_np, dpp_pp, dpp_sd,
    o_np, o_pp, o_sd,
    tt_np, tt_pp, tt_sd,
    exc_np, exc_pp, exc_sd,
    exc_minus_np, exc_minus_pp, exc_minus_sd,
    cross_check,
    adj_from_dict, dict_from_adj,
)
from .qk import qk_check_np, qk_check_pp, qk_check_sd, qk_min, qk_min_brute
