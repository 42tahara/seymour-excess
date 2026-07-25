# Note

The citable note accompanying this repository.

| file | what it is |
|---|---|
| `measuring-the-moat.tex` + `refs.bib` | **source of the current version (2.0)** |
| `measuring-the-moat-v2.1.pdf` | current version |
| `measuring-the-moat-v1.1.pdf` | version 1.1 (2026-07-23), archived under its own DOI |
| `note_draft_v1.tex`, `note_draft_v1.md`, `note_draft_v1.pdf` | the v1 line, frozen; not edited by v2 |
| `AUDIT_v1.md` | fact audit of v1 against the data ledger |
| `make_table.py` → `table_generated.tex` / `.md` | the measurement table, machine-generated from `data/` (**never hand-edit**) |
| `CHANGELOG.md` | version history |

Build: `tectonic -X compile measuring-the-moat.tex` (no local TeX
installation required; tectonic fetches what it needs).

## Which document is authoritative

**The note is.** Version 1.1 of this file said that the top-level README claim
table was authoritative "until v1.0 lands"; v1.0 and v1.1 have both landed and
that sentence was never updated, leaving two documents stating claims at
different versions. From version 2.0 onward the note is the authoritative
statement of what this repository asserts mathematically, and the README's
claim table is a navigational summary of it with the reproduction commands
attached. Where they disagree, the note is right and the README is a bug.
