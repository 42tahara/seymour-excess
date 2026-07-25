# Changelog

The note has its own, finer-grained changelog in `note/CHANGELOG.md`.

## v0.2.1 (2026-07-26)

**Correction.** v0.2.0 described the band `18 ≤ n ≤ 23` as having "no
construction". That is true of the family `G_n`, which needs `n ≥ 24`, and
false of the blow-up family `F`, whose smallest member has `n = 20`. The claim
was written before the smallest member of `F` was known — that came out of the
supervision round that corrected the emptiness remark in T9 — and was not
revisited afterwards.

- **New upper bounds** `E_{≥8}(20) ≤ 5`, `E_{≥8}(21) ≤ 6`, `E_{≥8}(22) ≤ 6`,
  `E_{≥8}(23) ≤ 6`, from blow-ups of the 5-vertex circulant tournament
  `C₅(1,2)`. Witnesses in `data/band/`, checked by `make verify-band`;
  `--full` re-derives that these are the minima over `F` and that `F` has no
  member at `n = 18` or `n = 19`.
- The band still has **no lower bound** and no search instrument that works
  in it. That part of the v0.2.0 description was accurate.

## v0.2.0 (2026-07-26)

**No claim of v0.1.0 became false.** Every published value was an upper bound,
and upper bounds do not become false when they improve; the one published
lower bound follows from the exact value proved here.

### Results

- **T7** `E_{δ≥8}(n) ≤ 3 + [3∤n]` for every `n ≥ 24`, from one explicit
  family. Subsumes every upper bound of v0.1.0: T1′'s `E(25)≤5, E(35)≤5,
  E(49)≤7` become 4, 4, 4, and O1's `E(50) ≤ 5` becomes 4.
- **T8** `E_{δ≥k}(2k+1) = 2k+1` for every `k ≥ 1`, by an elementary argument.
  The `k = 8` case supersedes v0.1.0's computer-assisted `E(17) ≥ 3`
  (CP-SAT, 357 s) and a later `≥ 5` (3,083 s) — both true, both weaker.
  Labelled **folklore**; it is stated because it replaces a solver run with a
  proof, not because it is new.
- **T9** a partial lower bound inside one explicitly defined class of
  capped-tournament blow-ups. **Not a lower bound on `E`.**
- **T6** extended to `7 ≤ n ≤ 30` (the `n = 29` row is now published) and
  moved into the note, which v0.1.0 did not cover.
- **M1** 77 measured witnesses, one per order `24 ≤ n ≤ 100`, all attaining
  the theorem value.

### Corrections to how things were said

- The note, not this README, is the authoritative statement of the
  mathematics. v0.1.0 had both stating claims at different versions.
- `E_δ` and `E_δ^sc` are now defined separately; v0.1.0's README defined the
  first, the note the second, and they were used interchangeably.
- "floor" is reserved for `E_δ(n)` itself. v0.1.0 applied it to values reached
  by search, 11 times.
- The reading of `E_δ(n)` as counting margin-0 vertices holds only for
  `3 ∣ n`.
- The n = 50 "three-point coincidence" is withdrawn as a question rather than
  answered: two of its three numbers were never minima.
- A structural reading of the two analysed excess-5 witnesses is withdrawn;
  both are now known to sit above the constructive value.

### Verification

- New targets `verify-t7`, `verify-t7-spec`, `verify-t8`, `verify-t9`,
  `verify-m1`; `verify-t7-spec` rebuilds the family from its written
  specification alone and scores it with the independent verifier.
- `check_hashes.py` now walks the witness subdirectories explicitly; before
  this, `--write` would silently have dropped 77 entries from the manifest.
- Guards in `make_table.py` and `blowup_sweep.py` were widened after negative
  controls showed they did not fire on real failure modes.
- Two shipped scripts used absolute paths that only resolved on the author's
  machine; fixed and checked from a foreign working directory.

## v0.1.0 (2026-07-23)

First public release. DOI 10.5281/zenodo.21497370.
