# The excess floor of Seymour's Second Neighbourhood Conjecture

> **v0.2.0 (draft — not yet released).** Supersedes
> [v0.1.0](https://doi.org/10.5281/zenodo.21497370) (2026-07-23), which
> remains permanently archived and citable. **No claim of v0.1.0 became
> false**; the upper bounds improved substantially, one lower bound turned
> out to be determinable exactly by hand, and the prose had drifted out of
> compliance with this repository's own verification protocol. See
> [What changed since v0.1.0](#what-changed-since-v010).

## Definitions

An **oriented graph** is a digraph with neither loops nor 2-cycles. For a
vertex v, `N⁺(v)` is the out-neighbourhood and `N⁺⁺(v)` is the set of
vertices reachable by exactly two arcs that are neither v itself nor members
of `N⁺(v)`; put `d(v) = |N⁺⁺(v)| − |N⁺(v)|` (the **margin**) and

```
excess(G) = Σ_v max(0, d(v) + 1).
```

Two minima are used in this repository and they must not be conflated:

```
E_δ(n)     = min excess over ALL n-vertex oriented graphs with min out-degree ≥ δ
E_δ^sc(n)  = min excess over the STRONGLY CONNECTED ones only
```

`E_δ(n) ≤ E_δ^sc(n)`, since the second minimises over a subclass. The
published note (v1.1, `note/`) defines its `E(n)` as `E_δ^sc(n)`; v0.1.0's
README stated the unrestricted one. **Every claim below holds for both**, and
the reason is stated per claim rather than left implicit: an upper bound
witnessed by a strongly connected graph bounds both minima, and an
infeasibility proof run without a connectivity constraint rules out the
larger class and therefore the subclass too.

We study δ = 8, the first open regime of Seymour's Second Neighbourhood
Conjecture (SSNC, 1990): `E_{δ≥8}(n) = 0` for some n would be a
counterexample to SSNC. This repository provides:

- **a constructive flat upper bound** — an explicit family G_n giving
  `E_{δ≥8}(n) ≤ 3 + [3∤n]` for every n ≥ 24 (T7),
- **the exact value at n = 17** — `E_{δ≥8}(17) = 17`, by a two-step
  argument requiring no solver (T8),
- **a class-limited partial lower bound** — inside one explicitly defined
  family of capped-tournament blow-ups, and **nowhere outside it** (T9),
- **a refutation of the Pisa structure conjecture**
  (arXiv:2601.21563, Conjecture 5.1) (T5),
- **finite verification of GKZ Conjecture 8.2** for k = 3 (T6), and
- **a measurement-methodology exhibit**: search attainment values that were
  wrong in *both* directions (M1, §Search attainment is not a floor).

## Terminology (read this before the tables)

This repository's verification protocol (`CLAUDE.md`) has stated from the
start:

> search attainment is an upper bound, not a floor (negative-control lesson)

The v0.1.0 prose did not comply with it: the README called values reached by
search a floor: the word occurs 11 times, three of them as the phrase "the
measured floor", others as "the floor" applied to a measured value. The
improvements below are what
made the non-compliance visible, but the rule was already ours. We now keep
three words apart, so that the text cannot drift from the protocol again:

| word | meaning | evidence value |
|---|---|---|
| **floor** | the number E_δ(n) itself — the exact minimum | **We do not know E_δ(n) exactly for a single n ≥ 18.** At n = 17 we do: it is 17 (T8) |
| **bound** | a proven inequality: an *upper* bound from an explicit verified witness, a *lower* bound from exhaustive or infeasibility argument | evidence |
| **attainment** | the best value some search actually reached | evidence for an **upper** bound only. **Never** evidence for a lower bound |

A search that fails to go below v establishes nothing about E_δ(n). This
repository contains two recorded instances of that failure mode pointing in
*opposite* directions (§Search attainment is not a floor).

## Claims and how to verify each one

Don't trust us — run the checks. Each claim maps to one command
(`make verify-all` for the fast set). Dependencies: `numpy` and `ortools`
only. All hashes are sha1 of the canonical adjacency JSON
(`verify/check_hashes.py` documents the convention).

Claim labels from v0.1.0 keep their meaning, so that citations of the
archived version stay unambiguous. New claims get new labels.

**Novelty labels.** Every claim carries one of *folklore* / *restatement of a
known result* / *new candidate*, because a verified claim and a novel claim are
different things and the table should not blur them:

| | label |
|---|---|
| **T8** (`E_{δ≥k}(2k+1) = 2k+1`) | **folklore.** Both steps are already in the published note v1.1 of this repository, which cites [GKZ, Lem. 2.2] for the second; and the argument is the classical fact that a vertex of maximum score in a tournament is a king (Landau), applied to a regular tournament, where *every* vertex qualifies and `N⁺⁺(v) = N⁻(v)` follows. (We have not traced the attribution to a primary source and do not cite one; the label does not depend on it, since the note's own citation settles it.) We state T8 because it replaces a solver run with a proof, **not** because it is new |
| **T7** (flat upper bound), **T9** (class-limited) | **new candidate** — no matching statement located in the literature; we make no priority claim |
| T5, T6 | as in v0.1.0 (refutation of a published conjecture; finite verification of a published conjecture) |

| # | Claim | Status | Verify with |
|---|---|---|---|
| **T7** | **E_{δ≥8}(n) ≤ 3 + [3∤n] for every n ≥ 24** — the explicit family G_n = C₃[s₀,s₁,s₂; c₀,c₁,c₂] (near-equal 3-layer ring, intra-layer transitive tournament truncated at a cap) is oriented, strongly connected, has δ⁺ = ⌊n/3⌋ ≥ 8, and excess exactly 3 + [3∤n] | theorem (constructive; full proof in `constructions/upper_bound_family.py` docstring, Lemmas 0–4) | `make verify-t7` |
| **T8** | **E_{δ≥k}(2k+1) = 2k+1 for every k ≥ 1**; in particular **E_{δ≥8}(17) = 17**. Moreover *every* oriented graph on 2k+1 vertices with δ⁺ ≥ k has excess exactly 2k+1 — the value is not a minimum over a varied class, it is the only value the class takes | **theorem, elementary, no solver** — a paper proof the reader can check on the spot; see below the table. *Remark:* the proof gives N⁺⁺(v) = N⁻(v), hence distance ≤ 2 from every vertex to every other, so these graphs are automatically strongly connected: `E_δ = E_δ^sc` at n = 2k+1, δ = k | `make verify-t8` (seconds) |
| **T9** | **class-limited partial lower bound — stated in full below the table, and not to be paraphrased.** Inside the family of capped-tournament blow-ups over a strongly connected oriented quotient on 3 ≤ m ≤ 6 vertices, every member with minimum out-degree ≥ 8 has excess ≥ 3, and excess = 3 forces 3 ∣ n | theorem, **restricted to that family** (integer feasibility with a per-instance derived bound B; no upper bound on n assumed) | `make verify-t9` (~4 min) |
| T7′ | (was **T1**) pure m-ring: E ≤ min{m≥3 : m∣n, n/m≥8} | theorem — **subsumed by T7 for n ≥ 24**; kept for provenance | `make verify-t1` |
| T7″ | (was **T1′**) C_m^k power ring, in particular E(25)≤5, E(35)≤5, E(49)≤7 | theorem candidate — **subsumed by T7** (which gives 4, 4, 4); never received supervision sign-off on its arithmetic | `make verify-t1p` |
| T2 | E_{δ≥8}(17) ≥ 3 (CP-SAT excess ≤ 2 INFEASIBLE, 357 s) | still true; **superseded by T8**, which is exact and elementary. Retained as a record of what the direct solver model reaches, not as a statement about n = 17 | `make verify-t2` (recorded log) |
| T5 | The Pisa structure conjecture (arXiv:2601.21563, Conj 5.1) is false: explicit counterexamples at n = 8, 48, 50 and a minimal one at n = 7 | verified, 3 independent implementations — unchanged | `make verify-t5` |
| T6 | GKZ Conjecture 8.2 (arXiv:2603.29626) holds for k = 3 for all n ≤ 28 and n = 30 | CP-SAT INFEASIBLE; non-vacuous (hypothesis graphs exist at every scanned n). **n = 29 is UNKNOWN in the published log** (14,400 s). A later INFEASIBLE run at 29,506 s exists but its record is not in `data/` at the time of writing; the row extends to n ≤ 30 only once that row is published here | `make verify-t6` |
| O1 | (was: evolved witnesses at n = 50) E(50) ≤ 5 via `champion_28da4a1e` | still true; **superseded by T7**, which gives E(50) ≤ 4. The witness is retained because §Structure analyses it | `make verify-o1` |
| M1 | **measurement, not a claim.** A pure-CPU hill-climbing sweep at all 77 orders 24 ≤ n ≤ 100 attained exactly 3 + [3∤n] at every one of them, and never below | upper-bound corroboration only; **no lower-bound content whatsoever** | `make verify-m1` (re-verifies the stored witnesses) |
| — | Every graph in `data/` matches its recorded hash | — | `make verify-hashes` |

### T8 in full

> **Proposition.** Let k ≥ 1. Every oriented graph G on n = 2k+1 vertices
> with minimum out-degree ≥ k satisfies excess(G) = n. Hence
> **E_{δ≥k}(2k+1) = 2k+1**, and in particular **E_{δ≥8}(17) = 17**.
>
> *Proof.* The arc count is at most C(n,2), and δ⁺ ≥ k forces it to be at
> least n·k = C(n,2); so equality holds and G is a regular tournament of
> out-degree k. Let v be any vertex and w ∈ N⁻(v). Suppose w ∉ N⁺⁺(v). For
> y ∈ N⁺(v) we have v → y, so y → w would make v → y → w a path of length two
> and put w in N⁺⁺(v); since G is a tournament, w → y instead. Hence
> N⁺(v) ⊆ N⁺(w); and w → v gives v ∈ N⁺(w) while v ∉ N⁺(v), so
> N⁺(v) ∪ {v} ⊆ N⁺(w) and |N⁺(w)| ≥ k+1 > k — a contradiction. Hence
> N⁻(v) ⊆ N⁺⁺(v) and |N⁺⁺(v)| ≥ k. On the other hand
> |N⁺⁺(v)| ≤ n − 1 − k = k. So d(v) = 0 at every vertex and excess = n. ∎

**The hypothesis δ⁺ ≥ k is exactly what carries this**, and dropping it by one
collapses the value rather than lowering it slightly: at n = 5, k = 2, the
oriented graph with out-sets {3,4}, {3,4}, {3}, {4}, {2} is digon-free with
δ⁺ = 1 and excess **3**, not 5 (`verify/verify_ssnc.py`). This is the
quantitative form of the warning below: n = 2k+1 with δ⁺ = k is a rigid,
isolated point, not a sample of how excess behaves nearby.

Two consequences worth stating plainly:

- **This replaces a solver run with a paper proof.** v0.1.0's T2
  (`E_{δ≥8}(17) ≥ 3`) rested on a CP-SAT INFEASIBLE run of 357 s, and a later
  run of 3,083 s pushed it to `≥ 5`. Both are true, and both are weaker than
  the two lines above. We record this rather than quietly dropping it: the
  computation was sound and the conclusion it reached was simply not the
  strongest available. `make verify-t8` now checks a *theorem*, in seconds,
  instead of replaying a solver log.
- **n = 17 is degenerate, and the large value must not be misread.** See
  [The state of the lower bound](#the-state-of-the-lower-bound).

### T9 in full

This is the whole claim. It is reproduced complete, including its last
paragraph, and should be quoted rather than summarised.

> **Definition.** Let H be a strongly connected oriented graph on m vertices,
> 3 ≤ m ≤ 6. For a vector of positive integers (n₁,…,n_m) and a vector of
> integers (c₁,…,c_m) with 0 ≤ c_a ≤ n_a, define the **capped-tournament
> blow-up** G = H[n; c] as follows. The vertex set is the disjoint union of
> classes C₁,…,C_m with |C_a| = n_a, whose elements are written
> u_{a,0},…,u_{a,n_a−1}. The arcs are of these two kinds only:
> **(R)** whenever H has a → b, then u_{a,j} → every vertex of C_b, for every
> j; **(T)** u_{a,j} → u_{a,l} for every pair (j, l) with l < min(j, c_a).
> Put n = Σ_a n_a. **Write F for the set of all G = H[n; c] arising this way
> whose minimum out-degree is at least 8**; this set, and nothing larger, is
> what the claim below quantifies over.
>
> **Claim — about the family F only; we do not quantify over arbitrary
> oriented graphs.** For every triple (H, n, c) as above **whose G has minimum
> out-degree at least 8** — that is, for every member of F — we have
> **excess(G) ≥ 3**, and if excess(G) = 3 then **3 ∣ n**. The quantification is
> over the members of F, with no bound on n.
>
> **This is not a lower bound on E_{δ≥8}(n).** Since most oriented graphs are
> not blow-ups of the above kind, this claim says nothing whatsoever about
> anything outside F.

Three things are worth spelling out. All three were mis-stated in earlier
drafts and corrected by definition gates — the third only at the last review,
after having been written down twice:

- **3 ≤ m ≤ 6, not m ≤ 6.** There is no strongly connected oriented graph on
  2 vertices (it would need a 2-cycle), and on 1 vertex the sole graph has no
  arcs at all, so every class out-sum is 0 and the minimum out-degree
  condition fails. Either way m = 1, 2 contribute nothing. The quotients
  actually enumerated number **4,313** (1 + 4 + 76 + 4,232 for m = 3, 4, 5, 6).
- **The claim carries no bound on n, and needs none.** It is decided by
  integer feasibility with a bound derived per instance, not by sweeping
  orders.
- **The smallest member of F has n = 20, not 24.** An earlier draft asserted
  that F is empty below 24; that assertion was **false**. Take the 5-vertex
  circulant tournament as quotient with all five classes of size 4: every class
  out-sum is 4 + 4 = 8, giving a strongly connected member with δ⁺ = 8 at
  **n = 20**. And 20 is optimal: minimising Σ n_a over *all* orientations of
  the quotient (dropping strong connectivity, which only enlarges the class,
  and using that adding arcs to H can only help the degree condition) returns
  24, 24, 20, 20 for m = 3, 4, 5, 6 — so no member has n < 20, and the n = 20
  witness attains it. (Two independent solvers, CP-SAT and a MILP, return the
  same four numbers.) The mistake was extrapolating the m = 3 case: for the
  directed triangle every vertex of H has out-degree 1, so δ⁺ ≥ 8 forces
  *every* class to have ≥ 8 vertices and hence n ≥ 24 — but for larger m a
  vertex of H has several out-neighbours whose class sizes need only *sum* to 8.
  The claim itself is unaffected: it quantifies over members of F, whatever n
  they have.

The unswept range: quotients on m ≥ 7 vertices, and every construction that
is not a capped-tournament blow-up — which is almost all of them.

Separately from the claim above, and not part of it: re-solving each order
individually gives minimum excess exactly 3 + [3∤n] over this family for
every 24 ≤ n ≤ 60.

## The state of the lower bound

This is the honest summary, and it is short:

- n = 17: **exact**, E = 17 (T8) — but degenerate, and the large value is
  the easiest thing in this repository to misread. The degree bound forces a
  regular tournament, so the class contains exactly one excess value and
  n = 17 carries **no** information about how E behaves where the class is
  rich: at n = 18 non-tournaments with low excess are immediately admissible.
  E(17) = 17 is not evidence for any lower bound anywhere else.
- 18 ≤ n ≤ 23: **nothing.** The family G_n needs n ≥ 24; no lower bound is
  known; the hill-climbing sweep does not function as an instrument in this
  band (out-degree density leaves almost no legal moves).
- n ≥ 24: **nothing.** `3 + [3∤n]` is an upper bound only. Whether it is
  exact is open, and the direct CP-SAT model does not reach the orders that
  matter (excess ≤ 3 is INFEASIBLE at n = 17 in 1,356 s, and UNKNOWN at
  n = 19 and n = 20 within 1,800 s each).

Any lower bound `E_{δ≥8}(n) ≥ 2` for all n is already a strengthening of
SSNC restricted to this class. We state no conjecture as "essentially
settled".

## Search attainment is not a floor

The methodological result of this project, and the reason for the
terminology table above. Search attainment was wrong in **both**
directions, and only explicit construction ever adjudicated:

- **too high.** Fresh search with all construction seeds withheld returned
  13 at n = 48 and 20 at n = 50, against construction bounds 3 and 5 at the
  same orders (pre-registered negative control). At n = 101…150, search
  attained 5–6 where T7 gives 3 or 4.
- **too low.** At n = 59 and n = 61 search settled on excess 7 and this was
  read as a "floor = ring length + 1" pattern at primes. It was a basin
  artefact: T7 gives 4. The hypothesis was pre-registered and is now
  **rejected**.

Consequently v0.2.0 reports construction bounds and search attainments in
separate columns everywhere, and the word "floor" is reserved for E_δ(n).

## Structure of two search-discovered witnesses at excess 5

`champion_28da4a1e` (n = 50, pentagon ring of five tight survivors) and
`champion_n53_ca40b396` (n = 53, keystone cluster with margins (+1,0,0,0))
have different architectures, different margin economies, and identical
local dynamics: no improving single flip, large neutral plateaus, and — for
the keystone — survival of an exhaustive 171,288-pair two-flip attack
**restricted to the cluster neighbourhood** (the note's qualifier, which must
not be dropped: this is not an unrestricted depth-2 search).

**T7 reframes what this means.** Both graphs have excess 5 at orders where
the construction gives 4 and 3. Their local rigidity is therefore rigidity
of a *non-optimal* point: it describes the basin, not the optimum. We
previously read it as "consistent with a global counting obstruction"; that
reading is withdrawn. The arc-slack identity and margin analysis in
`experiments/beast_trail/` are measurements of these specific graphs and
remain valid as such.

## A note on the Pisa framing

v0.1.0 stated that optimal and near-optimal graphs here have maximum margin
exactly 0, i.e. are Pisa graphs, so that E_δ(n) measures the minimum number
of margin-0 vertices such a graph must carry. **That gloss holds only when
3 ∣ n.** The family G_n at 3 ∤ n contains a vertex of margin +1 (excess 4 =
2 + 1 + 1 from margins +1, 0, 0), so it is not Pisa. The Pisa reading of
E_δ(n) is therefore a statement about the 3 ∣ n subsequence, not about E_δ
in general. Checked directly: `verify/check_t7_from_spec.py` rebuilds G_n
from the written specification alone and confirms, at all 37 orders
24 ≤ n ≤ 60, that the number of positive-margin vertices is 0 when 3 ∣ n and
1 when 3 ∤ n — together with the excess, the min out-degree ⌊n/3⌋, and strong
connectivity.

## Repository layout

```
note/            citable note (v2 in preparation; v1.1 published)
constructions/   upper_bound_family.py — the family G_n of T7, with the full
                 proof in its docstring and a --verify self-check;
                 pure_ring.py, power_ring.py (subsumed, kept for provenance);
                 transplant.py
blowup/          blowup_sweep.py (closed form + forward sweep),
                 blowup_inverse.py (T9: inverse solve, no bound on n),
                 verify_blowup_independent.py (four bounded cross-checks)
verify/          independent checkers (no code shared with the pipeline):
                 verify_ssnc.py, pisa_check.py, check_claims.py,
                 check_hashes.py, sensitivity.py, independent_fable.py
lib/dist2core/   shared invariant library, three implementations in agreement
data/            witness graphs (sha1-manifested), sweep tables,
                 CP-SAT logs (excess2_results.jsonl, excess3_probe_results.jsonl,
                 gkz82_*.jsonl), blow-up sweep records
experiments/     the search pipeline and the CP-SAT models
```

## Open problems & work in progress

Stated as of 2026-07-25. Naming an open question, with a date, is part of
what this repository claims.

1. **Is 3 + [3∤n] exact?** Equivalently: is E_{δ≥8}(n) ≥ 3 for all n, with
   equality when 3 ∣ n? We have **no lower-bound evidence at any n ≥ 18** —
   only the class-limited T9 and the fact that a broad sweep never got
   below the construction. The case "≥ 2 for all n" is the restriction to
   this class of a conjecture of Dara, Francis, Jacob and Narayanan
   (DAM 2022): every sink-free oriented graph has at least two Seymour
   vertices.
2. **The band 18 ≤ n ≤ 23.** No construction, no lower bound, no working
   search instrument. The smallest genuinely unexplored gap.
3. **Beyond the blow-up class.** T9 closes excess ≤ 2 inside F. What
   happens for quotients on m ≥ 7 vertices, and for constructions that are
   not blow-ups at all? The latter is the large unswept range.
4. **δ = 8 local feasibility.** The δ = 7 local INFEASIBLE argument
   (arXiv:2606.30588) does not extend directly: 12 of 340 rows of our
   δ = 8 generalisation are locally consistent (all in the b = 7, k = 3
   family), and **36 rows are undecided at withdrawal** — 16 still UNKNOWN
   after splitting, 20 never started.
5. **A certificate for infeasibility.** Every INFEASIBLE result here rests
   on the encoding (Appendix A of the note) and on solver soundness. A
   proof-logging solver would remove the second dependency. Note that T8
   removes it at n = 17 by dispensing with the solver entirely.
6. **GKZ Conjecture 8.2 beyond the scan.** k = 3 verified for n ≤ 28 and
   n = 30 by the logs published here. k ≥ 4 and a structural proof for
   k = 3 remain open.
7. **Tournaments with exactly two tight vertices.** Does a tournament with
   δ⁺ ≥ 8 and exactly two satisfied vertices, both tight, exist? Twelve
   one-hour CP-SAT attempts at 17 ≤ n ≤ 28 all returned UNKNOWN — and the
   n = 17 case is settled negatively by T8 before any computation.

## What changed since v0.1.0

v0.1.0 and its DOI are permanent. Nothing in it became false: every
published value was an upper bound, and upper bounds do not become false
when they improve; T2's `≥ 3` follows from T8's exact value.

| v0.1.0 | v0.2.0 | why |
|---|---|---|
| T1′: E(25) ≤ 5, E(35) ≤ 5, E(49) ≤ 7 | 4, 4, 4 | T7 |
| T2: E(17) ≥ 3, by CP-SAT (357 s) | E(17) = 17 exactly, **by an elementary proof**, as the k = 8 case of E_{δ≥k}(2k+1) = 2k+1 | T8 |
| O1: E(50) ≤ 5 | 4 | T7 |
| attainments E(40)→23, E(45)→21, E(60)→33 | 4, 3, 3 | T7 |
| a measured value called "the floor" at n = 50, n = 53 (twice as "the measured floor", four more times as "the floor") | attainment, not floor | the prose is brought into compliance with this repository's own protocol rule, which already said so |
| the n = 50 three-point coincidence (floor 5 = evolutionary optimum = survivor ring length) "still wants an explanation" | recorded as history: at the time, 5 looked minimal at n = 50, and three quantities agreeing at 5 looked like a phenomenon. A graph of excess 4 was then constructed, so two of the three numbers were never a minimum and there is no coincidence left to explain | T7 — the question is withdrawn, not answered |
| E_δ(n) "measures the minimum number of margin-0 vertices" | holds for 3 ∣ n only | G_n has a +1 margin vertex when 3 ∤ n |
| definition of E_δ(n) without strong connectivity (README) vs with it (note) | with strong connectivity, everywhere | the note's definition was the intended one; all witnesses are strongly connected and all lower bounds were proved for the larger class, so no value changes |
| search: LLM-driven program evolution | pure-CPU hill climbing | the classical search reached the same values faster and wider |

## Collaboration statement

This project is a human–AI collaboration. Direction, decisions, and
judgment: Daiki Tahara. Mathematical supervision, verification, and
literature work: Claude (Anthropic). Implementation, search, and
computation: Claude (Anthropic). All claims are machine-verified by
independent implementations; the mathematics should be judged on the
verifiability of the claims, not on the nature of the authors.

## Related work

- **Halkiewicz, arXiv:2601.21563** — introduces Pisa graphs and the
  structure conjecture; we refute Conjecture 5.1 (T5).
- **Guo–Kang–Zwaneveld, arXiv:2603.29626** — Seymour-tight orientations;
  their skeleton condition powers the (now subsumed) T7″ construction,
  their Lemma 2.2 is one step of T8, and we verify their Conjecture 8.2 for
  k = 3 in finite ranges (T6).
- **Dara–Francis–Jacob–Narayanan, DAM 2022** — conjecture that every
  sink-free oriented graph has at least two Seymour vertices; Open
  problem 1 is its restriction to this class.
- **arXiv:2606.30588 (with Kaneko–Locke 2001)** — minimum out-degree ≥ 8
  for any SSNC counterexample; this theorem is baked into E_δ's constraint.

## Cite as

> Daiki Tahara, *Measuring the moat: excess bounds near Seymour's second
> neighbourhood conjecture*, 2026.
> With Claude (Anthropic) as AI collaborators.
> Preprint DOI: [10.5281/zenodo.21497888](https://doi.org/10.5281/zenodo.21497888)
> --- Software/data DOI: [10.5281/zenodo.21497370](https://doi.org/10.5281/zenodo.21497370)

Both are concept DOIs and resolve to the newest version. To cite v0.1.0
specifically, use its version DOI from the Zenodo record.

## License

Code: MIT. Data (`data/`) and documents (`note/`): CC-BY 4.0. See `LICENSE`.
