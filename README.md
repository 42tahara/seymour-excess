# The excess floor of Seymour's Second Neighbourhood Conjecture

> **Status: pre-release staging.** The accompanying note (`note/`) is being
> finalised; wording of the definitions below will be aligned with it before
> v0.1.0.

We define the quantitative invariant

**E_δ(n)** — the minimum, over all n-vertex oriented graphs with minimum
out-degree ≥ δ, of the *excess* `Σ_v max(0, d(v)+1)`, where
`d(v) = |N⁺⁺(v)| − |N⁺(v)|` is the second-neighbourhood margin —

and study it for δ = 8, the first open regime of Seymour's Second
Neighbourhood Conjecture (SSNC, 1990): `E_{δ≥8}(n) = 0` for some n would be a
counterexample to SSNC. Optimal and near-optimal graphs here turn out to have
maximum margin exactly 0, i.e. they are *Pisa graphs* in the sense of
Halkiewicz (arXiv:2601.21563), so equivalently E_δ(n) measures the minimum
number of margin-0 vertices such a graph must carry. This repository provides:

- **constructive upper bounds** — pure m-rings and their C_m^k power-ring
  generalisation (skeleton idea from Guo–Kang–Zwaneveld, arXiv:2603.29626),
- **measured upper bounds** — LLM-driven evolutionary search (FunSearch-style),
- **computational lower bounds** — CP-SAT proofs (E_{δ≥8}(17) ≥ 3),
- **a refutation of the Pisa structure conjecture**
  (arXiv:2601.21563, Conjecture 5.1), and
- **finite verification of GKZ Conjecture 8.2** for k = 3.

## Claims and how to verify each one

Don't trust us — run the checks. Each claim maps to one command; all fast
checks together take seconds (`make verify-all`). Dependencies: `numpy` and
`ortools` only. All hashes are sha1 of the canonical adjacency JSON
(`verify/check_hashes.py` documents the convention).

| # | Claim | Status | Verify with |
|---|---|---|---|
| T1 | E_{δ≥8}(n) ≤ min{m≥3 : m\|n, n/m≥8} (pure m-ring) | theorem (constructive) | `make verify-t1` |
| T1′ | E_{δ≥8}(n) ≤ min{m≥3 : m\|n, ∃k≥1: 2k<m, k·(n/m)≥8} (C_m^k power ring; T1 is k=1). In particular E(25)≤5, E(35)≤5, E(49)≤7 | theorem candidate (arithmetic in `constructions/power_ring.py` docstring; numeric verification by 2 independent implementations) | `make verify-t1p` |
| T2 | E_{δ≥8}(17) ≥ 3 | theorem (CP-SAT proof, 219 s) | `make verify-t2` (recorded log) / `make verify-t2-full` (re-prove, ~4 min) |
| T5 | The Pisa structure conjecture (arXiv:2601.21563, Conj 5.1) is false: explicit counterexamples at n = 8, 48, 50 and a minimal one at n = 7 | verified, 3 independent implementations | `make verify-t5` |
| T6 | GKZ Conjecture 8.2 (arXiv:2603.29626) holds for k = 3 for all n ≤ 24 (scan to n = 30 in progress) | CP-SAT INFEASIBLE; non-vacuous (hypothesis graphs exist at every scanned n) | `make verify-t6` |
| O1 | Evolved witnesses: E_{δ≥8}(50) ≤ 5 (`champion_28da4a1e`, survivors form a directed pentagon); earlier ≤ 8 (`champion_d74d6509`) | verified graphs (independent checker) | `make verify-o1` |
| — | Every graph in `data/` matches its recorded hash | — | `make verify-hashes` |

Measured evolutionary upper bounds per n (not claims — search results;
see `data/en_sweep.json` for provenance): E(25)→12, E(30)→3, E(35)→7,
E(40)→23, E(45)→21, E(50)→5, E(60)→33, E(75)→3. Note the evolution hits the
ring bound exactly at n = 30, 50, 75 and spikes on the "divisor deserts"
(25, 35) that T1′ has since bridged constructively.

**Known-limits note.** The upper-bound curve (T1/T1′) is constructive; the
only proven lower bound is the single point T2. The equality
"floor = minimal legal skeleton size" is a working hypothesis, not a theorem.

## Repository layout

```
note/            citable PDF note (in preparation)
constructions/   pure_ring.py, power_ring.py — build + self-verify witnesses
verify/          independent checkers (no code shared with the pipeline):
                 verify_ssnc.py, pisa_check.py, check_claims.py,
                 check_hashes.py, sensitivity.py
data/            witness graphs (sha1-manifested), sweep table,
                 CP-SAT proof logs (excess2_results.jsonl, gkz82_*.jsonl)
experiments/     the full search pipeline (evolution, n-sweep, CP-SAT models)
                 — see experiments/README.md; requires an Anthropic API key
                 for the evolutionary parts, executes model-generated code
```

## In progress

Fresh divisor-desert probes (n = 49/50/53), the GKZ 8.2 scan beyond n = 23,
tournament-restricted excess ≤ 2 scans, and the δ = 8 local CP-SAT table are
running; their results will be appended to `data/` and the tables above.

## Related work

- **Halkiewicz, arXiv:2601.21563** — introduces Pisa graphs and the structure
  conjecture; we refute Conjecture 5.1 (T5) and quantify the margin-0
  population its objects must carry.
- **Guo–Kang–Zwaneveld, arXiv:2603.29626** — Seymour-tight orientations; their
  Thm 4.6/Lem 4.7 skeleton condition powers our T1′ construction, and we
  verify their Conjecture 8.2 for k = 3 in finite ranges (T6).
- **arXiv:2606.30588 (with Kaneko–Locke 2001)** — minimum out-degree ≥ 8 for
  any SSNC counterexample; this theorem is baked into E_δ's constraint and our
  δ = 8 CP-SAT models generalise that paper's δ = 7 local analysis.

## Cite as

> Daiki Tahara, *The excess floor of Seymour's conjecture: ring
> constructions and computational lower bounds*, 2026.
> With Claude (Anthropic) as AI collaborators.
> DOI: [Zenodo DOI — added at v0.1.0 release]

## License

Code: MIT. Data (`data/`) and documents (`note/`): CC-BY 4.0. See `LICENSE`.
