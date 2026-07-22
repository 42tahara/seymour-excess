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
| T2 | E_{δ≥8}(17) ≥ 3 | computer-assisted (CP-SAT infeasibility, 357 s; encoding + limitations in the note's Appendix A) | `make verify-t2` (recorded log) / `make verify-t2-full` (re-prove, ~6 min) |
| T5 | The Pisa structure conjecture (arXiv:2601.21563, Conj 5.1) is false: explicit counterexamples at n = 8, 48, 50 and a minimal one at n = 7 | verified, 3 independent implementations | `make verify-t5` |
| T6 | GKZ Conjecture 8.2 (arXiv:2603.29626) holds for k = 3 for all n ≤ 28 and n = 30 (n = 29 UNKNOWN at a 4-hour budget) | CP-SAT INFEASIBLE; non-vacuous (hypothesis graphs exist at every scanned n) | `make verify-t6` |
| O1 | Evolved witnesses: E_{δ≥8}(50) ≤ 5 (`champion_28da4a1e`, survivors form a directed pentagon); earlier ≤ 8 (`champion_d74d6509`) | verified graphs (independent checker) | `make verify-o1` |
| — | Every graph in `data/` matches its recorded hash | — | `make verify-hashes` |

Measured evolutionary upper bounds per n (not claims — search results;
see `data/en_sweep.json` for provenance): E(25)→12, E(30)→3, E(35)→7,
E(40)→23, E(45)→21, E(47)→9, E(49)→**6**, E(50)→5, E(53)→**5**, E(59)→7, E(60)→33, E(75)→3.
The evolution hits the ring bound exactly at n = 30, 50, 75 and spikes on
the "divisor deserts" (25, 35, 49) that T1′ has since bridged
constructively. The prime probe is the surprise: E_{δ≥8}(53) ≤ 5
(independently verified witness `champion_n53_ca40b396`, 3 margin-0 +
1 margin-1 vertices, min out-degree 17) — equal to the measured floor at
n = 50, with no ring construction available at a prime. The 2026-07-22 survey
added: E(49)≤6, beating the T1′ constructive bound of 7, and a δ-slide at
n = 50 showing the floor 5 unmoved under δ≥9 and δ≥10. Ring-seeded lineages
lost at every point surveyed (5 consecutive negative controls).

**Keystone transplant (same day):** surgically porting the n = 53
champion's survivor cluster (bulk deletion / cloning, cluster untouched;
`constructions/transplant.py`, deterministic greedy) gives
**E(47) ≤ 5 and E(59) ≤ 5** — the first prime bounds matching the n = 50/53
floor, superseding the evolutionary survey values 9 and 7 and resolving the
apparent "prime staircase" as pure search-reachability bias. The transplant
family also realises excess 4 with four margin-0 survivors at n = 57
(not a bound record there — T1 gives 3 at multiples of 3 — but the first
keystone graph with the +1 insurance eliminated). Witnesses:
`data/transplant_n{47,57,59}.json`, triple-verified; a 20-generation polish
run on each transplant found no improvement — the transplant values are
single-lineage local minima like every other point in this landscape.

**Known-limits note.** The upper-bound curve (T1/T1′) is constructive; the
only proven lower bound is the single point T2. The equality
"floor = minimal legal skeleton size" is a working hypothesis, not a theorem.

## Repository layout

```
note/            citable PDF note (in preparation)
constructions/   pure_ring.py, power_ring.py — build + self-verify witnesses
verify/          independent checkers (no code shared with the pipeline):
                 verify_ssnc.py, pisa_check.py, check_claims.py,
                 check_hashes.py, sensitivity.py, independent_fable.py
                 (the last written from definitions only by a third author —
                 three implementations, two authors, one graph)
data/            witness graphs (sha1-manifested), sweep table,
                 CP-SAT proof logs (excess2_results.jsonl, gkz82_*.jsonl)
experiments/     the full search pipeline (evolution, n-sweep, CP-SAT models)
                 — see experiments/README.md; requires an Anthropic API key
                 for the evolutionary parts, executes model-generated code
```

## Open problems & work in progress

Stated as of 2026-07-22. We record these questions deliberately: naming an
open question, with a date, is part of what this repository claims.

1. **Is E_{δ≥8}(n) ≥ 3 for every n ≥ 17?** We conjecture yes. Proven only
   at n = 17 (T2); the CP-SAT search for excess ≤ 2 at n = 18..22 exhausts
   its time budget undecided (`data/excess2_results.jsonl`). The
   tournament-restricted variant ran the full range n = 17..28: every
   instance hit its 1-hour budget undecided
   (`data/excess2_tournament.jsonl`; the n = 17 case is in fact INFEASIBLE
   by inheritance from T2, since tournaments are a subclass). Twelve
   budget-exhausted instances in a row: the conjecture is at least not
   cheaply refutable, even tournament-restricted.
2. **Does the floor equal the minimal legal skeleton size?** The measured
   floor at the prime n = 53 (excess 5, no legal skeleton) now **refutes
   the naive form** of this hypothesis: rings are sufficient for the floor
   where they exist, but not necessary. The surviving question is what
   invariant does control the floor — the n = 50 three-point coincidence
   (floor 5 = evolutionary optimum = survivor ring length) still wants an
   explanation.
3. **Do primes resist at all?** No: evolution reached a verified excess
   of 5 at n = 53, equal to the measured floor at n = 50, although T1′
   offers no construction there. What is the asymmetric structure that
   replaces the ring, and does an explicit prime-friendly construction
   exist? The witness has 3 margin-0 + 1 margin-1 vertices — not a clean
   ring pattern.
4. **δ = 8 local feasibility.** The δ = 7 local INFEASIBLE argument
   (arXiv:2606.30588) does not extend directly: 12 of 340 rows of our
   δ = 8 generalisation are locally consistent (all in the b = 7, k = 3
   family). Resolution of the remaining UNKNOWN rows is running.
5. **GKZ Conjecture 8.2 beyond the scan.** k = 3 verified for n ≤ 28
   and n = 30 (n = 29 hit a 4-hour budget undecided). k ≥ 4 and a
   structural proof for k = 3 remain open.

Results are appended to `data/` and the tables above as they complete.

## Collaboration statement

This project is a human–AI collaboration. Direction, decisions, and
judgment: Daiki Tahara. Mathematical supervision, verification, and
literature work: Claude (Fable, Anthropic). Implementation, search, and
computation: Claude (Code, Anthropic). All claims are machine-verified by
independent implementations; the mathematics should be judged on the
verifiability of the claims, not on the nature of the authors.

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
