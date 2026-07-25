## Table 1 — surveyed orders

| n | theorem 3+[3∤n] | earlier construction | fresh-search attainment | best stored witness (graph sha1) |
|---|---|---|---|---|
| 24 | 3 | 3 (ring m=3,k=1,t=8) | - | `2517130b` |
| 25 | 4 | 5 (ring m=5,k=2,t=5) | 12 | `150003fd` |
| 27 | 3 | 3 (ring m=3,k=1,t=9) | - | `5b5ae497` |
| 30 | 3 | 3 (ring m=3,k=1,t=10) | 3 | `feba34e7` |
| 35 | 4 | 5 (ring m=5,k=2,t=7) | 7 | `ca62560c` |
| 40 | 4 | 4 (ring m=4,k=1,t=10) | 23 | `9cb88021` |
| 45 | 3 | 3 (ring m=3,k=1,t=15) | 21 | `abd86a45` |
| 47 | 4 | 5 (keystone transplant) | 9 | `ccc19f2e` |
| 48 | 3 | 3 (ring m=3,k=1,t=16) | 13 (seed-free) | `d43ca1db` |
| 49 | 4 | 7 (ring m=7,k=2,t=7) | 6 | `db2e4026` |
| 50 | 4 | 5 (ring m=5,k=1,t=10) | 5 (20 seed-free) | `bce286aa` |
| 51 | 3 | 3 (ring m=3,k=1,t=17) | - | `e5d2d5eb` |
| 53 | 4 | 5 (keystone transplant) | 5 | `8562bd98` |
| 57 | 3 | 3 (ring m=3,k=1,t=19) | - | `d02d73a9` |
| 59 | 4 | 5 (keystone transplant) | 7 | `d90d86c3` |
| 60 | 3 | 3 (ring m=3,k=1,t=20) | 33 | `44b4bca8` |
| 75 | 3 | 3 (ring m=3,k=1,t=25) | 3 | `63346a8f` |

## Table 2 — measurement summary (data/sonar_best/)

| quantity | value |
|---|---|
| orders covered | 24..100, no gaps |
| stored witnesses | 77 (one per order) |
| excess = 3+[3∤n] | 77 of 77 orders |
| orders disagreeing | none |
| min out-degree observed | 8 (n=24) .. 33 (n=99) |
| strongly connected | 77 of 77 orders |

Regenerated 2026-07-26; every excess, out-degree and connectivity value above is recomputed from the adjacency lists by verify/verify_ssnc.py (see also verify/check_m1.py), and hashes are canonical adjacency sha1 checked against data/manifest.json by verify/check_hashes.py. The earlier constructions are listed to show them being superseded: no row falls below the theorem value. n=24 is the boundary case with minimum out-degree exactly 8. n=57: the transplant family also realises 4 (all survivors tight), not a bound record. The 77 witnesses are upper-bound witnesses only; nothing here is a lower bound.
