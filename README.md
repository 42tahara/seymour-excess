# The excess floor of Seymour's Second Neighbourhood Conjecture

> **v0.2.0.** Supersedes [v0.1.0](https://doi.org/10.5281/zenodo.21497370)
> (2026-07-23), which remains permanently archived and citable. **No claim of
> v0.1.0 became false**: every published value was an upper bound, and upper
> bounds do not become false when they improve. See
> [What changed since v0.1.0](#what-changed-since-v010).

**The note is the authoritative statement of what this repository asserts**
— `note/measuring-the-moat-v2.0.pdf`. This README is a map of it with the
reproduction commands attached. Where the two disagree, the note is right and
this file is a bug. (Version 1.1 of the note left this the other way round by
accident; see `note/README.md`.)

## Definitions

An **oriented graph** is a digraph with neither loops nor 2-cycles. For a
vertex v, `N⁺(v)` is the out-neighbourhood and `N⁺⁺(v)` the set of vertices
reachable by exactly two arcs that are neither v itself nor members of
`N⁺(v)`; put `d(v) = |N⁺⁺(v)| − |N⁺(v)|` (the **margin**) and

```
excess(G) = Σ_v max(0, d(v) + 1).
```

Two minima are used here and must not be conflated:

```
E_δ(n)     = min excess over ALL n-vertex oriented graphs with min out-degree ≥ δ
E_δ^sc(n)  = min excess over the STRONGLY CONNECTED ones only
```

`E_δ(n) ≤ E_δ^sc(n)`, since the second minimises over a subclass. Note v1.1
defined only the second and called it `E`; v0.1.0's README defined only the
first; the two were used interchangeably. Every claim below holds for both,
and the reason is stated per claim rather than left implicit: an upper bound
witnessed by a strongly connected graph bounds both, and an infeasibility
argument run without a connectivity constraint rules out the larger class and
hence the subclass too.

We study δ = 8, the first open regime of Seymour's Second Neighbourhood
Conjecture (SSNC, 1990): `E_{δ≥8}(n) = 0` for some n would be a counterexample
to SSNC.

## Terminology: floor, bound, attainment

v0.1.0's README used "floor" for values reached by search. It was already
against the project's own rule that a search attainment is an upper bound and
not a floor, and the improvements in this version are what made the
non-compliance visible. The count is checkable, so here is the command rather
than only the number:

```bash
git show v0.1.0:README.md | grep -o -i floor | wc -l     # 11
```

Three of the eleven are the phrase "the measured floor" (collapse newlines
first: one of them straddles a line break), four more are "the floor" applied
to a measured value, and the first is the title. Three words are now kept
apart:

| word | meaning | evidence value |
|---|---|---|
| **floor** | `E_δ(n)` itself — the exact minimum | **We do not know it at a single n ≥ 18.** At n = 17 we do: it is 17 (T8) |
| **bound** | a proved inequality: an *upper* bound from an explicit verified witness, a *lower* bound from an exhaustive or infeasibility argument | evidence |
| **attainment** | the best value some search actually reached | evidence for an **upper** bound only. **Never** for a lower bound |

A search that fails to go below v establishes nothing about `E_δ(n)`. This
repository records two instances of that failure mode pointing in *opposite*
directions ([below](#search-attainment-is-not-a-floor)).

## Claims, where they are proved, and how to check them

Don't trust us — run the checks. `make verify-all` runs the fast set in a few
seconds. Dependencies: `numpy` and `ortools`. Hashes are sha1 of the canonical
adjacency JSON (`verify/check_hashes.py` documents the convention).

Claim labels from v0.1.0 keep their meaning so that citations of the archived
version stay unambiguous; new claims get new labels.

| # | Claim | Proved in | Novelty | Verify with |
|---|---|---|---|---|
| **T7** | `E_{δ≥8}(n) ≤ E^sc_{δ≥8}(n) ≤ 3 + [3∤n]` for every **n ≥ 24**, from one explicit family `G_n` | note Thm 2.6 (Lemmas 2.1–2.5) | new candidate | `make verify-t7`, `make verify-t7-spec` |
| **T8** | `E_{δ≥k}(2k+1) = E^sc_{δ≥k}(2k+1) = 2k+1` for every **k ≥ 1**; in particular `E_{δ≥8}(17) = 17`. Every admissible graph at those orders has excess exactly 2k+1 — it is the only value the class takes | note Prop 3.1 | **folklore** — see below | `make verify-t8` |
| **T9** | class-limited partial lower bound inside one explicitly defined family of capped-tournament blow-ups. **Not a lower bound on `E`** — see [below](#t9-in-full) | note Thm 4.1, App. B | new candidate | `make verify-t9` (~2 min) |
| T7′ | (was **T1**) pure m-ring: `E ≤ min{m≥3 : m∣n, n/m≥8}` | note §2.3 | subsumed by T7 | `make verify-t1` |
| T7″ | (was **T1′**) cycle-power ring; in particular `E(25)≤5, E(35)≤5, E(49)≤7` | note §2.3 | subsumed by T7 (which gives 4, 4, 4) | `make verify-t1p` |
| T2 | `E_{δ≥8}(17) ≥ 3` (CP-SAT, `exc ≤ 2` INFEASIBLE, 357 s) | note §3.3 | superseded by T8, which is exact and elementary | `make verify-t2` |
| T5 | The Pisa structure conjecture (arXiv:2601.21563, Conj 5.1) is false: counterexamples at n = 8, 48, 50 and a minimal one at n = 7 | note Rmk 6.2 | refutation of a published conjecture | `make verify-t5` |
| T6 | GKZ Conjecture 8.2 (arXiv:2603.29626) holds for k = 3 for all 7 ≤ n ≤ 30 | note Prop 3.3 | finite verification of a published conjecture | `make verify-t6` |
| O1 | (was: evolved witnesses at n = 50) `E(50) ≤ 5` via `champion_28da4a1e` | note §6, Rmk 6.1 | superseded by T7 (which gives 4); the witness is kept because §6 analyses it | `make verify-o1` |
| M1 | **measurement, not a claim.** A pure-CPU sweep attained exactly `3 + [3∤n]` at all 77 orders 24 ≤ n ≤ 100, and never below | note §5.1, Table 2 | upper-bound corroboration only; **no lower-bound content** | `make verify-m1` |
| — | every graph in `data/` matches its recorded hash | — | — | `make verify-hashes` |

**Why T8 is labelled folklore.** Both steps are already in note v1.1 of this
repository, which cites [GKZ, Lem. 2.2] for the second; the argument is the
classical fact that a vertex of maximum score in a tournament reaches every
other within two steps, applied to a regular tournament where every vertex
qualifies. We have not traced the attribution to a primary source and do not
cite one — the label does not depend on it, since the note's own citation
settles it. T8 is stated because it **replaces a solver run with a proof**,
not because it is new: v0.1.0's T2 rested on 357 s of CP-SAT and a later run
of 3,083 s pushed the same statement to `≥ 5`. Both are true; both are weaker
than six lines of argument. `make verify-t8` now checks a theorem in under a
second instead of replaying a log.

### T9 in full

Reproduced verbatim from the note, Appendix B, including its last paragraph.
Quote it; do not summarise it.

> **Definition.** Let H be a strongly connected oriented graph on m vertices,
> 3 ≤ m ≤ 6. For a vector of positive integers (n₁,…,n_m) and a vector of
> integers (c₁,…,c_m) with 0 ≤ c_a ≤ n_a, define the **capped-tournament
> blow-up** G = H[n; c] as follows. The vertex set is the disjoint union of
> classes C₁,…,C_m with |C_a| = n_a, whose elements are written
> u_{a,0},…,u_{a,n_a−1}. The arcs are of these two kinds only: **(R)** whenever
> H has a → b, then u_{a,j} → every vertex of C_b, for every j; **(T)**
> u_{a,j} → u_{a,l} for every pair (j,l) with l < min(j, c_a). Put n = Σ_a n_a.
> Write **F** for the set of all such G whose minimum out-degree is at least 8.
>
> **Claim — about F only; we do not quantify over arbitrary oriented graphs.**
> Every G ∈ F satisfies excess(G) ≥ 3, and if excess(G) = 3 then 3 ∣ n. The
> quantification is over the members of F, with no bound on n.
>
> **This is not a lower bound on `E_{δ≥8}(n)`.** Since most oriented graphs
> are not blow-ups of the above kind, this claim says nothing whatsoever about
> anything outside F.

Three points, all of which were mis-stated in earlier drafts and corrected by
definition gates — the third only at the final review, after being written
down twice:

- **3 ≤ m ≤ 6, not m ≤ 6.** There is no strongly connected oriented graph on
  two vertices, and on one vertex the sole graph has no arcs and so fails the
  degree condition; either way m = 1, 2 contribute nothing. The quotients
  enumerated number **4,313** = 1 + 4 + 76 + 4,232 for m = 3, 4, 5, 6. (These
  counts were re-derived independently with `nauty`: `geng -c m | directg -o`
  followed by a strong-connectivity filter gives 1, 4, 76, 4232.)
- **The claim carries no bound on n and needs none.** It is decided by integer
  feasibility with a bound derived per instance, not by sweeping orders.
- **The smallest member of F has n = 20, not 24.** An earlier draft asserted
  that F is empty below 24; that was **false**. Take the 5-vertex circulant
  tournament as quotient with all five classes of size 4: every class out-sum
  is 4 + 4 = 8, giving a strongly connected member with δ⁺ = 8 at n = 20. And
  20 is optimal: minimising Σ n_a over all orientations of the quotient
  returns 24, 24, 20, 20 for m = 3, 4, 5, 6. The mistake was extrapolating the
  m = 3 case, where each quotient vertex has out-degree 1 and the degree bound
  forces *every* class to have ≥ 8 vertices. The claim itself is unaffected: it
  quantifies over members of F, whatever n they have.

The unswept range: quotients on m ≥ 7 vertices, and every construction that is
not a capped-tournament blow-up — which is almost all of them.

## The state of the lower bound

Short, because there is little to say:

- **n = 17: exact**, `E = 17` (T8) — but degenerate, and the easiest thing
  here to misread. The degree bound forces a regular tournament, so the class
  takes exactly one excess value, and n = 17 carries **no** information about
  how E behaves where the class is rich: at n = 18 non-tournaments of low
  excess are immediately admissible. Dropping the degree bound by one collapses
  the value rather than lowering it — at n = 5, k = 2 there is a digon-free
  graph with δ⁺ = 1 and excess 3, not 5. `E(17) = 17` is not evidence for a
  lower bound anywhere else.
- **18 ≤ n ≤ 23: nothing.** No construction (`G_n` needs n ≥ 24), no lower
  bound, and no working search instrument — the density forced by δ⁺ ≥ 8
  leaves almost no legal local moves.
- **n ≥ 24: nothing.** `3 + [3∤n]` is an upper bound only; whether it is exact
  is open. The direct CP-SAT model does not reach the orders that matter:
  `exc ≤ 3` is INFEASIBLE at n = 17 in 1,356 s and UNKNOWN at n = 19 and
  n = 20 within 1,800 s each.

Any bound `E_{δ≥8}(n) ≥ 2` for all n is already a strengthening of SSNC
restricted to this class. Nothing here is described as "essentially settled".

## Search attainment is not a floor

The methodological result of the project. Attainment was wrong in **both**
directions, and construction alone adjudicated each time (note §5.2).

- **Too high.** A pre-registered control — fresh search on the composites
  n = 48, 50 with all construction seeds withheld — returned 13 and 20 against
  construction values 3 and 5 at the same orders. The seed, not the search, had
  been carrying the composite values. Above the surveyed band the gap is
  narrower but persists: over the 50 orders 101 ≤ n ≤ 150 the best stored
  witness matches `3 + [3∤n]` at 40 of them and stands above it at 10,
  attaining 5 or 6 against a construction value of 4, the largest shortfall
  being +2. Those 50 witnesses ship in `data/sonar_high/` and the sentence is
  re-derived from them by `make verify-m1-high`; none of them falls *below*
  the construction, which the checker treats as a hard failure rather than a
  count, since it would be a new bound rather than a shortfall.
- **Too low.** At the primes n = 59 and n = 61 an earlier search settled on
  excess 7, read as a "floor = ring length + 1" pattern at primes. It was a
  basin artefact; the pre-registered hypothesis is **rejected**, the
  construction gives 4 at both, and witnesses of excess 4 at both are stored.
  Note the shape of the error: the search did not merely fail to reach the
  bound, it produced a value consistent enough across two orders to look like
  a law.

## Provenance of the solver logs

Not uniform, and a reader comparing claims should know which tier each rests
on (note §3.4). Measured field by field:

| log | rows | fields/row | model hash | solver version | workers |
|---|---|---|---|---|---|
| `data/gkz82_results.jsonl` (T6) | 25 | 7, and 6 on the three oldest rows | 0 | 0 | 0 |
| `data/excess2_results.jsonl` (T2) | 8 | 4, and 7 on one row | 1 | 1 | 0 |
| `data/excess3_probe_results.jsonl` (reachability) | 4 | 13 | 4 | 4 | 4 |

None of the three records a solver seed.

All models are in this repository and can be re-run; only the third log pins
down the binary that produced it. Two rows record a status changing on re-run,
and they are not the same phenomenon: n = 29 in the GKZ scan went UNKNOWN at
14,400 s then INFEASIBLE at 29,506 s (a budget was exhausted, roughly twice
the budget decided it), while n = 17 at cap 2 went UNKNOWN at 900 s then
INFEASIBLE at **218.9 s** — the deciding run was four times *faster*, so the
budget was not what was missing, and the rows do not record what differed.
Both rows are kept.

## A note on the Pisa framing

v0.1.0 said that optimal and near-optimal graphs here have maximum margin 0,
i.e. are Pisa graphs, so that `E_δ(n)` counts the margin-0 vertices such a
graph must carry. **That holds only when 3 ∣ n.** At 3 ∤ n the family `G_n`
contains a vertex of margin +1 (excess 4 = 2 + 1 + 1), so it is not Pisa.
Checked directly: `verify/check_t7_from_spec.py` rebuilds `G_n` from the
written specification alone and confirms, at all 37 orders 24 ≤ n ≤ 60, that
the positive-margin count is 0 when 3 ∣ n and 1 when 3 ∤ n — along with the
excess, the minimum out-degree ⌊n/3⌋, and strong connectivity.

## Repository layout

```
note/            the citable note — AUTHORITATIVE. measuring-the-moat.tex is
                 the v2.0 source; the v1.1 PDF is archived alongside it
constructions/   upper_bound_family.py — the family G_n of T7, with the full
                 proof in its docstring and a --verify self-check;
                 pure_ring.py, power_ring.py, transplant.py (subsumed, kept
                 for provenance)
blowup/          blowup_sweep.py (closed form + forward sweep),
                 blowup_inverse.py (T9: inverse solve, no bound on n),
                 verify_blowup_independent.py (four bounded cross-checks)
verify/          independent checkers, sharing no code with the pipeline:
                 verify_ssnc.py, pisa_check.py, check_claims.py,
                 check_hashes.py, check_m1.py, check_t7_from_spec.py,
                 check_t8.py, sensitivity.py, independent_fable.py
lib/dist2core/   shared distance-2 encoding and invariant library, every
                 invariant in three independent implementations.  It also
                 carries encodings for two other conjectures (Sullivan 2006
                 and small quasi-kernel); **this repository makes no claim
                 about either** — the code is shared because splitting it
                 would create two copies that drift
data/            witness graphs (sha1-manifested): sonar_best/ has one best
                 witness per order 24..100, sonar_high/ one per order
                 101..150; plus sweep tables, solver logs, blow-up records
experiments/     the search pipeline and the CP-SAT models
docs/            the review trail: supervision findings (SHOKEN_*), the claim
                 report they audited, and the cross-lineage review transcripts
```

## Open problems

Stated as of 2026-07-26. Naming an open question, with a date, is part of what
this repository claims.

1. **Is `3 + [3∤n]` exact?** Equivalently, is `E_{δ≥8}(n) ≥ 3` for all n with
   equality when 3 ∣ n? There is **no lower-bound evidence at any n ≥ 18** —
   only the class-limited T9, and the fact that a broad sweep never went below
   the construction. The case "≥ 2 for all n" is the restriction to this class
   of a conjecture of Dara, Francis, Jacob and Narayanan (DAM 2022).
2. **The band 18 ≤ n ≤ 23.** No construction, no lower bound, no working
   search instrument. The smallest genuinely unexplored gap.
3. **Beyond the blow-up class.** T9 closes `exc ≤ 2` inside F. What happens
   for quotients on m ≥ 7 vertices, and for constructions that are not
   blow-ups at all?
4. **δ = 8 local feasibility.** The δ = 7 local INFEASIBLE argument
   (arXiv:2606.30588) does not extend directly: in a δ = 8 generalisation of
   it, 12 of 340 rows are locally consistent (all in the b = 7, k = 3 family)
   and 36 rows are undecided — 16 still UNKNOWN after splitting, 20 never
   started. **The row-level log for this is not published here**, so unlike
   everything else in this README the figures are not checkable from this
   repository; treat them as a statement of where the work stopped, not as a
   verified result.
5. **A certificate for infeasibility.** Every INFEASIBLE result here rests on
   an encoding argument and on solver soundness. A proof-logging solver would
   remove the second dependency; T8 removes it at n = 17 by dispensing with
   the solver.
6. **GKZ Conjecture 8.2 beyond the scan.** k = 3 verified for n ≤ 30. k ≥ 4
   and a structural proof for k = 3 remain open.
7. **Tournaments with exactly two tight vertices.** Does a tournament with
   δ⁺ ≥ 8 and exactly two satisfied vertices, both tight, exist? Twelve
   one-hour CP-SAT attempts at 17 ≤ n ≤ 28 all returned UNKNOWN, and the
   n = 17 case is settled negatively by T8 before any computation.

## What changed since v0.1.0

v0.1.0 and its DOI are permanent, and nothing in it became false: every
published value was an upper bound, and T2's `≥ 3` follows from T8's exact
value.

| v0.1.0 | v0.2.0 | why |
|---|---|---|
| T1′: E(25) ≤ 5, E(35) ≤ 5, E(49) ≤ 7 | 4, 4, 4 | T7 |
| T2: E(17) ≥ 3, by CP-SAT (357 s) | E(17) = 17 exactly, by an elementary proof, as the k = 8 case of `E_{δ≥k}(2k+1) = 2k+1` | T8 |
| O1: E(50) ≤ 5 | 4 | T7 |
| attainments E(40)→23, E(45)→21, E(60)→33 | 4, 3, 3 | T7 |
| a measured value called "the floor" (11 occurrences) | attainment, not floor | the prose is brought into line with the project's own rule, which already said so |
| the n = 50 three-point coincidence "still wants an explanation" | recorded as history: at the time 5 looked minimal at n = 50 and three quantities agreeing at 5 looked like a phenomenon. A graph of excess 4 was then constructed, so two of the three numbers were never a minimum and there is no coincidence left to explain | T7 — the question is withdrawn, not answered |
| `E_δ(n)` "measures the minimum number of margin-0 vertices" | holds for 3 ∣ n only | `G_n` has a +1 margin vertex when 3 ∤ n |
| one symbol `E`, defined without strong connectivity in the README and with it in the note | `E_δ` and `E_δ^sc` defined separately; each claim says which it bounds | the two were being used interchangeably; no value changes, but the statements were ambiguous |
| the README claim table was the authoritative statement | the note is; the README maps it | note v1.1 said authority would pass to the note "until v1.0 lands", and that sentence was never updated after v1.0 landed |
| search: LLM-driven program evolution | pure-CPU hill climbing | the classical search reached the same values faster and over more orders |

## Collaboration statement

This project is a human–AI collaboration. Direction, decisions, and judgment:
Daiki Tahara. Mathematical supervision, verification, literature work,
implementation, search and solver engineering: Claude (Anthropic). All claims
are machine-verified by independent implementations; the mathematics should be
judged on the verifiability of the claims, not on the nature of the authors.

## Related work

- **Halkiewicz, arXiv:2601.21563** — introduces Pisa graphs and the structure
  conjecture; we refute Conjecture 5.1 (T5).
- **Guo–Kang–Zwaneveld, arXiv:2603.29626** — Seymour-tight orientations; their
  skeleton condition powers the (now subsumed) T7″ construction, their
  Lemma 2.2 is one step of T8, and we verify their Conjecture 8.2 for k = 3 in
  finite ranges (T6).
- **Dara–Francis–Jacob–Narayanan, DAM 2022** — conjecture that every sink-free
  oriented graph has at least two Seymour vertices; open problem 1 is its
  restriction to this class.
- **arXiv:2606.30588 (with Kaneko–Locke 2001)** — minimum out-degree ≥ 8 for
  any SSNC counterexample; this theorem is baked into `E_δ`'s constraint.

## Cite as

> Daiki Tahara, *Measuring the moat: excess bounds near Seymour's second
> neighbourhood conjecture*, 2026.
> With Claude (Anthropic) as AI collaborators.
> Preprint DOI: [10.5281/zenodo.21497888](https://doi.org/10.5281/zenodo.21497888)
> --- Software/data DOI: [10.5281/zenodo.21497370](https://doi.org/10.5281/zenodo.21497370)

Both are concept DOIs and resolve to the newest version. To cite v0.1.0 or
note v1.1 specifically, use the version DOI from the corresponding Zenodo
record.

## License

Code: MIT. Data (`data/`) and documents (`note/`): CC-BY 4.0. See `LICENSE`.
