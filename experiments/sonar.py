#!/usr/bin/env python3
"""Fish-finder (sonar): pure-CPU terrain survey of the E(n) upper-bound curve.

No LLM involved. For each n in a sweep range, run count-capped hill climbing
(equal-score acceptance, i.e. neutral drift allowed, plus optional random
kicks on stall) from three seed families:

  ring:k   k near-equal layers, complete bipartite to the next layer,
           impure vertex -> own pure vertex (h9 generalised to non-divisors,
           so prime n gets ring seeds too)
  rand:s   out-degree (delta+1) random digraph, seeded deterministically
  graft:i  champion transplant: nearest-n champion from data/champion_*.json
           and data/transplant_*.json, padded / trimmed to n, degree-patched

The scorer is an INDEPENDENT parameterised mirror of evaluate.py (which fixes
N at import time and therefore cannot sweep); `--selftest` cross-checks the
two implementations per the two-implementation protocol (HANDOFF section 8).

The goal is the RELATIVE terrain (prime bands vs composite bands, mod
fingerprints, mass-testing the "floor = ring length + 1" hypothesis), not
certified values. LLM evolution dives only where the fish shadows are dense.

Every finished restart is appended to data/sonar_results.jsonl immediately
(observations do not exist until saved); per-n best matrices go to
data/sonar_best/.  Resumable: logged (n, seed) pairs are skipped.  A PID lock
refuses double starts.

This is the tool that produced the measured witnesses in data/sonar_best/
(claim M1); verify/check_m1.py re-scores them with the independent verifier.
The run log data/sonar_results.jsonl is not shipped -- only the per-n best.

Usage (from the repository root):
  python3 experiments/sonar.py --selftest
  python3 experiments/sonar.py [--n-lo 40] [--n-hi 100] [--workers 4]
  python3 experiments/sonar.py --report
"""
import argparse
import glob
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time

import numpy as np

try:
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

BASE = os.path.dirname(os.path.abspath(__file__))   # experiments/ (evaluate.py)
DATA = os.path.join(os.path.dirname(BASE), 'data')
RESULTS = os.path.join(DATA, 'sonar_results.jsonl')
BEST_DIR = os.path.join(DATA, 'sonar_best')
LOCK = os.path.join(BASE, 'sonar.lock')


# ---------------------------------------------------------------- scoring
def scc_max(Ab):
    n = len(Ab)
    if HAVE_SCIPY:
        _, labels = connected_components(csr_matrix(Ab), directed=True,
                                         connection='strong')
        return int(np.bincount(labels).max())
    R = Ab | np.eye(n, dtype=bool)
    for _ in range(int(np.ceil(np.log2(n))) + 1):
        R = (R.astype(np.uint8) @ R.astype(np.uint8)) > 0
    return int((R & R.T).sum(axis=1).max())


def margins(A):
    # float32 matmul (BLAS) instead of evaluate.py's int32 matmul (generic
    # loop, ~50x slower): entries are 0/1 so every dot product is an integer
    # <= n, exact in float32 up to 2**24, hence reach2 is bit-identical.
    n = len(A)
    Ab = A.astype(bool)
    out1 = A.sum(axis=1, dtype=np.int32)
    reach2 = (A.astype(np.float32) @ A.astype(np.float32)) > 0
    n2 = (reach2 & ~Ab & ~np.eye(n, dtype=bool)).sum(axis=1)
    return n2.astype(np.int32) - out1


def score_n(A, delta=8):
    """(total, nsat, excess, minout, sccmiss) — parameterised evaluate.score."""
    n = len(A)
    if np.diag(A).any() or (A & A.T).any():
        return None
    d = margins(A)
    out1 = A.sum(axis=1, dtype=np.int32)
    nsat = int((d >= 0).sum())
    excess = int(np.maximum(0, d + 1).sum())
    degdef = int(np.maximum(0, delta - out1).sum())
    sccmiss = n - scc_max(A.astype(bool))
    return (1000000 * degdef + 10000 * sccmiss + excess,
            nsat, excess, int(out1.min()), sccmiss)


def partial_total(A, delta):
    """total without the sccmiss term — a LOWER bound on the true total."""
    d = margins(A)
    out1 = A.sum(axis=1, dtype=np.int32)
    excess = int(np.maximum(0, d + 1).sum())
    degdef = int(np.maximum(0, delta - out1).sum())
    return 1000000 * degdef + excess


# ---------------------------------------------------------------- seeds
def seed_ring(n, k):
    sizes = [n // k + (1 if c < n % k else 0) for c in range(k)]
    starts = [sum(sizes[:c]) for c in range(k + 1)]
    A = np.zeros((n, n), dtype=np.int8)
    for c in range(k):
        lo, hi = starts[c], starts[c + 1]
        nlo, nhi = starts[(c + 1) % k], starts[(c + 1) % k + 1]
        for u in range(lo, hi):
            A[u, nlo:nhi] = 1
        for w in range(lo + 1, hi):
            A[w, lo] = 1
    return A


def seed_random(n, rng, delta=8):
    A = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in rng.permutation(n):
            if int(A[i].sum()) >= delta + 1:
                break
            if j != i and not A[j, i]:
                A[i, j] = 1
    return A


def load_champion_pool():
    """[(n, A, source_path)] from data/champion_*.json, valid only."""
    pool = []
    files = (glob.glob(os.path.join(DATA, 'champion_*.json'))
             + glob.glob(os.path.join(DATA, 'transplant_*.json')))
    for f in sorted(files):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        adj = d.get('adj', d if all(k.isdigit() for k in d) else None)
        if not isinstance(adj, dict) or not adj:
            continue
        try:
            nn = int(d.get('N') or
                     max(max((int(k) for k in adj), default=-1),
                         max((v for vs in adj.values() for v in vs),
                             default=-1)) + 1)
            A = np.zeros((nn, nn), dtype=np.int8)
            for i, outs in adj.items():
                A[int(i), list(map(int, outs))] = 1
        except (ValueError, TypeError, IndexError):
            continue
        if np.diag(A).any() or (A & A.T).any():
            continue
        pool.append((nn, A, os.path.basename(f)))
    return pool


def patch_outdeg(A, rng, delta=8):
    n = len(A)
    for i in range(n):
        for j in rng.permutation(n):
            if int(A[i].sum()) >= delta:
                break
            if j != i and not A[i, j] and not A[j, i]:
                A[i, j] = 1
    return A


def seed_graft(n, src_A, rng, delta=8):
    A = src_A.copy()
    while len(A) > n:                      # trim the most-satisfied vertex
        v = int(np.argmax(margins(A)))
        keep = [i for i in range(len(A)) if i != v]
        A = A[np.ix_(keep, keep)]
    while len(A) < n:                      # duplicate a random vertex
        m = len(A)
        u = int(rng.integers(m))
        B = np.zeros((m + 1, m + 1), dtype=np.int8)
        B[:m, :m] = A
        B[m, :m] = A[u]                    # copy u's out-arcs
        for w in np.nonzero(A[:, u])[0]:   # in-arcs of u, coin-flipped
            if rng.random() < 0.5 and not B[m, w]:
                B[w, m] = 1
        A = B
    return patch_outdeg(A, rng, delta)


# ---------------------------------------------------------------- climb
def propose(A, out1, rng, delta):
    n = len(A)
    for _ in range(64):
        i, j = rng.integers(n), rng.integers(n)
        if i == j:
            continue
        if A[i, j]:
            if out1[i] <= delta:
                continue
            return ('rev' if rng.random() < 0.4 else 'del', int(i), int(j))
        if not A[j, i]:
            return ('add', int(i), int(j))
    return None


def apply_move(A, out1, mv):
    kind, i, j = mv
    if kind == 'del':
        A[i, j] = 0; out1[i] -= 1
    elif kind == 'add':
        A[i, j] = 1; out1[i] += 1
    else:
        A[i, j] = 0; A[j, i] = 1; out1[i] -= 1; out1[j] += 1


def revert_move(A, out1, mv):
    kind, i, j = mv
    if kind == 'del':
        A[i, j] = 1; out1[i] += 1
    elif kind == 'add':
        A[i, j] = 0; out1[i] -= 1
    else:
        A[j, i] = 0; A[i, j] = 1; out1[j] -= 1; out1[i] += 1


def climb(A0, rng, delta=8, budget=40000, stall_cap=8000,
          kicks=3, kick_size=8):
    """Sideways-accepting hill climb with random kicks on stall.

    Acceptance is total_new <= total_cur (neutral drift).  The sccmiss term
    is only computed when the cheap lower bound already passes — flips that
    worsen degdef/excess are rejected without an SCC pass.
    """
    A = A0.copy()
    out1 = A.sum(axis=1, dtype=np.int32)
    cur = score_n(A, delta)
    if cur is None:
        raise ValueError('invalid seed matrix')
    best, bestA = cur, A.copy()
    evals, stall = 0, 0
    while evals < budget:
        if stall >= stall_cap:
            if kicks <= 0:
                break
            kicks -= 1
            A, out1 = bestA.copy(), bestA.sum(axis=1, dtype=np.int32)
            for _ in range(kick_size):
                mv = propose(A, out1, rng, delta)
                if mv:
                    apply_move(A, out1, mv)
            s = score_n(A, delta)
            if s is None:                  # should not happen; be safe
                A, out1 = bestA.copy(), bestA.sum(axis=1, dtype=np.int32)
                s = best
            cur, stall = s, 0
            continue
        mv = propose(A, out1, rng, delta)
        if mv is None:
            break
        apply_move(A, out1, mv)
        evals += 1
        pt = partial_total(A, delta)
        if pt > cur[0]:                    # true total >= pt > cur: reject
            revert_move(A, out1, mv)
            stall += 1
            continue
        s = score_n(A, delta)
        if s[0] <= cur[0]:
            cur = s
            if s[0] < best[0]:
                best, bestA = s, A.copy()
                stall = 0
            else:
                stall += 1
        else:
            revert_move(A, out1, mv)
            stall += 1
    return bestA, best, evals


# ---------------------------------------------------------------- analysis
RING_MAX = 14      # Hamiltonicity is exponential; bigger survivor sets are
                   # nowhere near a floor configuration anyway (observed: no
                   # ring ever above |S|=8) and are reported as no ring.


def _ham_cycle(hard, soft, k, max_soft, budget=200000):
    """Hamiltonian cycle through all k vertices, or None.

    hard[v] / soft[v] are successor bitmasks; at most max_soft soft arcs may
    be used.  Depth-first with a step budget (k <= RING_MAX keeps this cheap).
    """
    full = (1 << k) - 1
    path, steps = [0], [0]

    def dfs(v, visited, used_soft):
        if steps[0] >= budget:
            return None
        steps[0] += 1
        if visited == full:
            if (hard[v] & 1) or (used_soft < max_soft and soft[v] & 1):
                return list(path)
            return None
        for w in range(k):
            bit = 1 << w
            if visited & bit:
                continue
            if hard[v] & bit:
                nsoft = used_soft
            elif (soft[v] & bit) and used_soft < max_soft:
                nsoft = used_soft + 1
            else:
                continue
            path.append(w)
            got = dfs(w, visited | bit, nsoft)
            if got is not None:
                return got
            path.pop()
        return None

    return dfs(0, 1, 0)


def detect_ring(A, S):
    """(ring_len, ring_kind) of the survivor set S: is it one closed ring?

    A ring is a directed cycle visiting EVERY survivor.  Two kinds:
      'direct'   the cycle uses arcs of A only (n=50 champion 28da4a1e: the
                 survivors 8->16->23->36->47->8 are a pentagon)
      'closed2'  the survivors form a chain in A that closes through a single
                 second-neighbourhood step (n=59 champion 24dc568c:
                 42->40->51->6->11->20 in A, closed by 20 ~~> 42 in N++)
    Chords are allowed (a permutation matrix is not required).  Branching
    survivor DAGs are not rings: n61 8ead9b5d ({0,6}->13->26->{37,47}) has two
    sources inside S, hence not even a Hamiltonian chain -> (None, None).
    """
    k = len(S)
    if k < 2 or k > RING_MAX:
        return None, None
    sub = A[np.ix_(S, S)].astype(bool)
    hard = [sum(1 << j for j in range(k) if sub[i, j]) for i in range(k)]
    if _ham_cycle(hard, [0] * k, k, 0) is not None:
        return k, 'direct'
    n = len(A)
    Ab = A.astype(bool)
    reach2 = (A.astype(np.float32) @ A.astype(np.float32)) > 0
    n2 = reach2 & ~Ab & ~np.eye(n, dtype=bool)
    sub2 = n2[np.ix_(S, S)]
    soft = [sum(1 << j for j in range(k) if sub2[i, j]) for i in range(k)]
    if _ham_cycle(hard, soft, k, 1) is not None:
        return k, 'closed2'
    return None, None


def analyze(A):
    d = margins(A)
    S = [int(v) for v in np.nonzero(d >= 0)[0]]
    ring_len, ring_kind = detect_ring(A, S)
    return {'survivors': {str(v): int(d[v]) for v in S},
            'ring_len': ring_len, 'ring_kind': ring_kind}


def graph_sha1(A):
    adj = {int(i): [int(j) for j in np.nonzero(A[i])[0]] for i in range(len(A))}
    return adj, hashlib.sha1(
        json.dumps(adj, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------- driver
def seed_jobs(n, pool, delta=8):
    jobs = [('ring', k) for k in range(3, min(8, n // delta) + 1)]
    jobs += [('rand', s) for s in (0, 1)]
    grafts = sorted((p for p in pool if 0 < abs(p[0] - n) <= 6 or p[0] == n),
                    key=lambda p: (abs(p[0] - n),))[:2]
    jobs += [('graft', src) for _, _, src in grafts]
    return jobs


def run_job(task):
    n, kind, param, delta, budget, stall_cap = task
    rng = np.random.default_rng(
        int(hashlib.sha1(f'{n}/{kind}/{param}'.encode()).hexdigest()[:8], 16))
    if kind == 'ring':
        A0 = seed_ring(n, param)
    elif kind == 'rand':
        A0 = seed_random(n, rng, delta)
    else:
        src = next(p for p in run_job.pool if p[2] == param)
        A0 = seed_graft(n, src[1], rng, delta)
    t0 = time.time()
    bestA, best, evals = climb(A0, rng, delta, budget, stall_cap)
    row = {'n': n, 'seed': f'{kind}:{param}', 'delta': delta,
           'score': list(best), 'excess': best[2], 'evals': evals,
           'wall': round(time.time() - t0, 1), **analyze(bestA)}
    return row, bestA


def _init_worker(pool):
    run_job.pool = pool


def save_best(n, A, best):
    os.makedirs(BEST_DIR, exist_ok=True)
    adj, gsha = graph_sha1(A)
    path = os.path.join(BEST_DIR, f'n{n}_excess{best[2]}_{gsha[:8]}.json')
    tmp = path + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump({'N': n, 'score': list(best), 'delta': 8,
                   'sha1_kind': 'adjacency_json', 'graph_sha1': gsha,
                   'source': 'sonar', 'adj': adj}, fh)
    os.replace(tmp, path)
    return path


def sweep(args):
    if os.path.exists(LOCK):
        pid = int(open(LOCK).read().strip() or 0)
        try:
            os.kill(pid, 0)
            sys.exit(f'sonar already running (pid {pid}); refusing double start')
        except (ProcessLookupError, ValueError):
            print(f'stale lock (pid {pid} gone), taking over')
    open(LOCK, 'w').write(str(os.getpid()))
    try:
        done = set()
        if os.path.exists(RESULTS):
            for line in open(RESULTS):
                try:
                    r = json.loads(line)
                    done.add((r['n'], r['seed']))
                except json.JSONDecodeError:
                    pass
        pool = load_champion_pool()
        print(f'champion pool: {len(pool)} graphs; resume: {len(done)} '
              f'restarts already logged')
        tasks = []
        for n in range(args.n_lo, args.n_hi + 1):
            for kind, param in seed_jobs(n, pool, args.delta):
                if (n, f'{kind}:{param}') not in done:
                    tasks.append((n, kind, param, args.delta,
                                  args.budget, args.stall))
        print(f'{len(tasks)} restarts to run, {args.workers} workers')
        best_seen = {}      # n -> excess, over rows logged this run + prior
        for line in open(RESULTS) if os.path.exists(RESULTS) else []:
            try:
                r = json.loads(line)
                if r.get('score', [1])[0] < 10000:   # degdef/scc clean only
                    best_seen[r['n']] = min(
                        best_seen.get(r['n'], 10**9), r['excess'])
            except json.JSONDecodeError:
                pass
        out = open(RESULTS, 'a')
        with mp.Pool(args.workers, _init_worker, (pool,)) as mpp:
            for row, bestA in mpp.imap_unordered(run_job, tasks):
                out.write(json.dumps(row) + '\n')
                out.flush()
                clean = row['score'][0] < 10000
                if clean and row['excess'] < best_seen.get(row['n'], 10**9):
                    best_seen[row['n']] = row['excess']
                    p = save_best(row['n'], bestA, tuple(row['score']))
                    print(f"n={row['n']:3d} NEW BEST excess {row['excess']:3d} "
                          f"({row['seed']}, ring {row['ring_len']}) -> "
                          f"{os.path.basename(p)}")
                else:
                    print(f"n={row['n']:3d} {row['seed']:12s} "
                          f"excess {row['excess']:3d} ring {row['ring_len']} "
                          f"({row['evals']} evals, {row['wall']}s)")
        print('sweep done.')
    finally:
        os.remove(LOCK)


# ---------------------------------------------------------------- selftest
def selftest():
    """Cross-check score_n against evaluate.py (independent implementation)."""
    snippet = ('import json,sys,numpy as np,evaluate;'
               'A=np.array(json.load(sys.stdin),dtype=np.int8);'
               'print(json.dumps(list(evaluate.score(A))))')
    rng = np.random.default_rng(0)
    fails = 0
    for n in (40, 50, 61, 97):
        mats = [seed_ring(n, 4), seed_random(n, rng)]
        A = seed_random(n, rng)
        for _ in range(60):                # random walk off the clean region
            mv = propose(A, A.sum(axis=1, dtype=np.int32), rng, 0)
            if mv:
                apply_move(A, A.sum(axis=1, dtype=np.int32), mv)
        mats.append(A)
        split = seed_ring(n, 4)            # closed out-set: sccmiss >> 0
        split[n // 2:, :n // 2] = 0        # (scipy SCC vs evaluate's squaring)
        mats.append(split)
        src = seed_random(n, rng)          # near-source vertex: sccmiss == 1
        src[:, 0] = 0; src[0, :] = 0; src[0, 1] = 1
        mats.append(src)
        for i, M in enumerate(mats):
            mine = score_n(M)
            env = dict(os.environ, SEYMOUR_N=str(n), SEYMOUR_DELTA='8')
            ref = json.loads(subprocess.run(
                [sys.executable, '-c', snippet], input=json.dumps(M.tolist()),
                capture_output=True, text=True, env=env, cwd=BASE,
                check=True).stdout)
            ok = list(mine) == ref
            fails += (not ok)
            print(f'n={n} mat{i}: sonar {list(mine)} evaluate {ref} '
                  f'{"OK" if ok else "MISMATCH"}')
    t0 = time.time()
    A = seed_ring(97, 5)
    for _ in range(200):
        score_n(A)
    print(f'\nscore_n speed at n=97: {(time.time()-t0)/200*1000:.2f} ms/eval')
    sys.exit(1 if fails else 0)


# ---------------------------------------------------------------- report
def is_prime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def report():
    best = {}
    for line in open(RESULTS):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get('score', [10**9])[0] >= 10000:
            continue
        if r['n'] not in best or r['excess'] < best[r['n']]['excess']:
            best[r['n']] = r
    print(' n     E<=  ring kind     floor=ring+1?  seed          divisors')
    for n in sorted(best):
        r = best[n]
        rl = r['ring_len']
        mark = ('YES' if rl is not None and r['excess'] == rl + 1 else
                'ring=E' if rl is not None and r['excess'] == rl else '')
        divs = [d for d in range(2, n) if n % d == 0]
        tag = 'prime' if is_prime(n) else f'div {divs[:6]}'
        print(f'{n:3d} {r["excess"]:6d} {rl if rl is not None else "-":>5} '
              f'{str(r.get("ring_kind") or "-"):8s} {mark:>13}  '
              f'{r["seed"]:12s}  {tag}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-lo', type=int, default=40)
    ap.add_argument('--n-hi', type=int, default=100)
    ap.add_argument('--delta', type=int, default=8)
    ap.add_argument('--budget', type=int, default=40000)
    ap.add_argument('--stall', type=int, default=8000)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.report:
        report()
    else:
        sweep(args)


if __name__ == '__main__':
    main()
