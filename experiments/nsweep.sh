#!/bin/zsh
# n-scaling sweep: measure E(n) = min excess and r(n) = min max-ratio per n.
# Each n gets its own DB so floors are comparable across independent runs.
# Usage: ANTHROPIC_API_KEY=... ./nsweep.sh [generations per n]   (default 40)
set -e
cd "$(dirname "$0")"
GENS=${1:-40}
for n in 25 30 35 40 45 60 75; do
    echo "=== SEYMOUR_N=$n ($GENS generations) ==="
    SEYMOUR_N=$n SEYMOUR_DB="evolve_n${n}.json" python3 -u evolve.py "$GENS" \
        2>&1 | tee "evolve_n${n}.log"
    SEYMOUR_N=$n SEYMOUR_DB="evolve_n${n}.json" python3 - <<'EOF'
import json, os
import numpy as np
from evaluate import score, N
from analyze import max_ratio
db = json.load(open(os.environ['SEYMOUR_DB']))
best = min((e for isl in db['islands'] for e in isl), key=lambda e: e['score'][0])
ns = {'np': np, 'N': N, 'score': score}
exec(best['code'], ns)
A = np.asarray(ns['construct']()).astype(int)
m, mx = int(A.sum()), N * (N - 1) // 2
print(f"n={N}: E(n)={best['score'][2]}  r(n)={max_ratio(A):.3f}  "
      f"tournament-proximity m/C(n,2)={m/mx:.3f}  (best total {best['score'][0]})")
EOF
done
echo "=== sweep done; run analyze.py with SEYMOUR_N/SEYMOUR_DB per n for details ==="
