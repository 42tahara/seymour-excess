# Changelog — Measuring the moat

## v2.0 (2026-07-26)
Integrated revision. **No claim of v1.1 became false**: every published value
was an upper bound, and upper bounds do not become false when they improve.

- **New (Thm 2.6)** the flat upper bound `E_{δ≥8}(n) ≤ 3 + [3∤n]` for every
  `n ≥ 24`, from one explicit family. Subsumes the pure-ring, cycle-power and
  keystone-transplant bounds of v1.1, which are kept as provenance (§2.3).
- **Replaced (Prop 3.1)** v1.1's computer-assisted `E(17) ≥ 3` (CP-SAT, 357 s)
  by the elementary `E_{δ≥k}(2k+1) = 2k+1` for all `k ≥ 1`. The solver runs
  are demoted to a record of where the direct model reaches (§3.3).
- **New (Thm 4.1, App. B)** a partial lower bound restricted to one explicitly
  defined class of capped-tournament blow-ups. Not a lower bound on `E`.
- **Definitions** `E_δ` and `E_δ^sc` are now separated. v1.1 defined only the
  strongly connected minimum while the repository README defined only the
  other, and the two were used interchangeably.
- **Terminology** "floor" is reserved for `E` itself. v1.1 applied it to
  values reached by search, which is what the improvements above made visible.
- **Withdrawn** the reading in §6 that the local rigidity of the two analysed
  witnesses was "consistent with a global counting obstruction": both are now
  known to sit above the constructive value, so the rigidity is that of a
  search basin.
- **Disclosed (§3.4)** the solver logs are not uniform in provenance; the
  section states field by field what each records.
- **Moved into the note (Prop 3.3)** the finite verification of GKZ
  Conjecture 8.2 for k = 3, which v1.1 carried only in the repository README.
- **Authority** the note, not the README, is the authoritative statement; see
  `note/README.md`.

## v1.1 (2026-07-23)
Add citation to Dara–Francis–Jacob–Narayanan (DAM 2022); reposition Problem 1
and Prop 4.1 relative to their conjecture. No mathematical content changed.

## v1.0 (2026-07-23)
First public release. Version DOI 10.5281/zenodo.21497889 — confirmed
against DataCite, which records it with `version: 1.0` and
`IsVersionOf 10.5281/zenodo.21497888`. The concept DOI 21497888 resolves to
the newest version, which was 1.1 before this release.
