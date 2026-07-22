# Experiments — the search pipeline

Everything in this directory *produces* results; nothing here is needed to
*verify* them (that is `verify/`'s job, with independent implementations).

## Components

- `evaluate.py` — deterministic judge. score = 10⁶·degdef + 10⁴·sccmiss +
  excess; `SEYMOUR_N` selects n (default 50). The degdef term encodes the
  theorem that any SSNC counterexample has min out-degree ≥ 8.
- `evolve.py` — FunSearch-style loop: a cheap LLM mutates genome programs,
  the judge scores them; 3-island model with migration and periodic
  strategy memos from a stronger model. `SEYMOUR_DB` selects the lineage DB.
- `gen0.py` — seed genomes. `analyze.py` — histograms, max-ratio.
- `nsweep.sh` — per-n independent runs measuring the E(n) curve.
- `funnel_mutant.py` — the "interest on deficit relocation" experiment.
- `gkz_conj82.py` — GKZ Conjecture 8.2 finite verifier (CP-SAT).
- `delta8/` — CP-SAT models: `excess2_search.py` (direct excess ≤ cap
  search, `--tournament` mode), `gen_delta.py` (δ-generalised local model,
  `--delta 7 --validate` reproduces the published δ=7 table),
  `split_unknowns.py` (eBC/eUB split resolver for UNKNOWN rows).

## Reproduction

```bash
pip install anthropic numpy ortools
export ANTHROPIC_API_KEY=...          # evolutionary parts only
python3 gen0.py                       # seed scores
SEYMOUR_N=50 python3 evolve.py 100    # ~300 cheap-model calls per 100 gens
python3 delta8/excess2_search.py --n 17 --cap 2   # T2 in ~4 minutes
python3 gkz_conj82.py --scan 7 12
```

CP-SAT runs are seeded (`random_seed = 1`); INFEASIBLE results are sound by
model design (constraints only ever relaxed), FEASIBLE outputs are always
re-checked exactly in numpy before being reported.

## ⚠️ Security

`evolve.py` executes model-generated Python locally. The namespace is
restricted, but treat it as untrusted code: run in a container or disposable
environment.

## What is deliberately not included

Raw lineage databases (`evolve_db*.json`) and run logs are excluded from the
public repository. They are reproducible artifacts, and excluding them keeps
the repo free of incidental environment details. The distilled results
(champions, sweep table, proof logs) live in `data/` with hashes.
