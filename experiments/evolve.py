"""FunSearch-style evolution loop for Seymour second-neighbourhood counterexamples.

Cheap model (Haiku) mutates programs; deterministic evaluator judges;
island model with periodic migration; occasional smart-model analysis.
Requires: pip install anthropic numpy;  ANTHROPIC_API_KEY or `ant auth login`.
Usage: python3 evolve.py [generations]  (state persists in evolve_db.json)

SECURITY NOTE: this executes model-generated Python locally. Run it in a
container/VM or at least a throwaway user account. The exec namespace is
restricted, but treat it as untrusted code anyway.
"""
import builtins, hashlib, inspect, json, os, re, signal, sys
import numpy as np
from evaluate import score, N

GENERATIONS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
DB_PATH = os.environ.get('SEYMOUR_DB', 'evolve_db.json')
ISLANDS = 3
TOP_K = 3                 # exemplars shown to the mutator
POP_CAP = 12
MIGRATE_EVERY = 10
ANALYZE_EVERY = 15        # smart-model strategy note frequency
MUTATOR_MODEL = os.environ.get('MUTATOR_MODEL', 'claude-haiku-4-5')
ANALYST_MODEL = os.environ.get('ANALYST_MODEL', 'claude-sonnet-4-6')
TIMEOUT_S = 30            # per-candidate execution budget

TASK = f"""You are evolving Python programs that construct a directed graph
attacking Seymour's Second Neighbourhood Conjecture (open since 1990) by
searching for a counterexample: an oriented graph (no loops, no 2-cycles)
where EVERY vertex v has |N++(v)| < |N+(v)| strictly (N+ = out-neighbours,
N++ = vertices at directed distance exactly 2).
Write ONE function `construct()` returning a numpy ({N},{N}) 0/1 matrix A,
A[i,j]=1 meaning arc i->j, zero diagonal, no 2-cycles (never A[i,j]=A[j,i]=1).
numpy is available as np; you may also import math/itertools/random.
Deterministic seeds preferred.
Score = 1000000*degdef + 10000*sccmiss + excess. The PRIMARY objective is
excess = sum_v max(0, |N++(v)|-|N+(v)|+1): it is 0 exactly when every vertex
is strictly deficient, i.e. a counterexample, and unlike counting satisfied
vertices it rewards shaving margin off ANY vertex. degdef punishes every
vertex whose out-degree is below 8; sccmiss counts vertices outside the
largest strongly connected component. Lower is better; 0 refutes the
conjecture. TWO HARD REQUIREMENTS: (a) every vertex must have out-degree >= 8
(theorem: any counterexample has min out-degree >= 8; sinks trivially satisfy
the conjecture, so low-degree tricks are useless and heavily penalised);
(b) the graph must be strongly connected (a minimal counterexample has no
proper closed out-set — otherwise the closed module would be a smaller
counterexample — so the search space is provably strongly connected digraphs).
Known experimental fact: moving deficit around costs margin elsewhere (a
tournament+funnel rewiring of the best block killed its survivors but blew
excess up 17 -> 111 downstream), and the best genomes sit on plateaus: no
single arc flip lowers total excess, but many flips are excess-NEUTRAL. So in
any local search you write, ACCEPT equal-score moves (use <=, never <) and
take several neutral steps before judging a direction dead — coordinated
2-3 flip sequences through the plateau are where improvements live. Budget
discipline: cap every local-search loop by ITERATION COUNT (at most ~4000
score() calls total), never by wall-clock time — the judge kills any candidate
at 30 seconds, and counted loops survive where timed loops die. The open
question is whether ANY structure lowers total excess below the current
record. Other known facts:
random digraphs satisfy the conjecture easily; balanced circulants/Cayley
graphs land on the all-ties plateau (every d(v)=0, nsat={N}); UNBALANCED cyclic
structures concentrate the satisfying vertices into one small class (see
exemplars) — the frontier is breaking that last class with asymmetric,
non-algebraic structure. Be creative; improve on the exemplars; do not copy
them. Return ONLY a Python code block."""

def llm(model, prompt, max_tokens=4000):
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=max_tokens,
                                 messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in msg.content if b.type == "text")

def extract_code(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return m.group(1) if m else text

ALLOWED_MODULES = {'numpy', 'math', 'itertools', 'random', 'functools',
                   'collections', 'heapq'}

def safe_import(name, *args, **kwargs):
    if name.split('.')[0] in ALLOWED_MODULES:
        return builtins.__import__(name, *args, **kwargs)
    raise ImportError(f"import of {name!r} is blocked")

SAFE_BUILTINS = {name: getattr(builtins, name) for name in (
    'range', 'len', 'int', 'float', 'abs', 'min', 'max', 'sum', 'sorted',
    'set', 'list', 'dict', 'tuple', 'enumerate', 'zip', 'print', 'bool',
    'bin', 'any', 'all', 'str', 'isinstance', 'map', 'filter', 'round',
    'pow', 'divmod', 'reversed', 'frozenset', 'iter', 'next', 'repr',
    'hash', 'type', 'ValueError', 'TypeError', 'IndexError', 'KeyError',
    'ZeroDivisionError', 'StopIteration', 'Exception')}
SAFE_BUILTINS['__import__'] = safe_import

class Timeout(Exception):
    pass

def run_candidate(code):
    def handler(signum, frame):
        raise Timeout()
    ns = {'np': np, 'numpy': np, 'N': N, 'score': score,
          '__builtins__': dict(SAFE_BUILTINS)}
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(TIMEOUT_S)
    try:
        exec(code, ns)
        return score(ns['construct']())
    finally:
        signal.alarm(0)

def shrink_loops(code, factor=10):
    """Timeout rescue: divide large iteration counts by `factor` instead of
    discarding the candidate — heavy searches are good genes, just too slow."""
    return re.sub(r'range\((\d{4,})\)',
                  lambda m: f'range({int(m.group(1)) // factor})', code)

def code_key(code):
    return hashlib.sha1(code.encode()).hexdigest()

def add_entry(island, entry):
    keys = {code_key(e['code']) for e in island}
    if code_key(entry['code']) not in keys:
        island.append(entry)

def seed_functions():
    import gen0
    for name, fn in sorted(vars(gen0).items()):
        if name.startswith('h') and callable(fn):
            lines = inspect.getsource(fn).splitlines()
            lines[0] = 'def construct():'
            yield '\n'.join(lines)

def load_db():
    if os.path.exists(DB_PATH):
        return json.load(open(DB_PATH))
    db = {'gen': 0, 'islands': [[] for _ in range(ISLANDS)], 'notes': []}
    for i, code in enumerate(seed_functions()):
        try:
            s = run_candidate(code)
            if s is not None:
                add_entry(db['islands'][i % ISLANDS],
                          {'code': code, 'score': list(s), 'gen': 0})
        except Exception as ex:
            print(f"seed {i} failed: {type(ex).__name__}: {ex}")
    return db

def save_db(db):
    tmp = DB_PATH + '.tmp'
    json.dump(db, open(tmp, 'w'))
    os.replace(tmp, DB_PATH)

def exemplars(island):
    return sorted(island, key=lambda e: e['score'][0])[:TOP_K]

def main():
    db = load_db()
    print(f"start: gen {db['gen']}, island sizes {[len(i) for i in db['islands']]}")
    for g in range(db['gen'] + 1, db['gen'] + 1 + GENERATIONS):
        for isl_i, island in enumerate(db['islands']):
            ex = exemplars(island)
            if not ex:
                continue
            shown = "\n\n".join(
                f"# score {e['score'][0]} (nsat {e['score'][1]}/excess {e['score'][2]}"
                f"/minout {e['score'][3]}/sccmiss {e['score'][4]})\n{e['code']}"
                for e in ex)
            note = db['notes'][-1] if db['notes'] else ""
            prompt = f"{TASK}\n\nStrategy note:\n{note}\n\nExemplars:\n{shown}"
            try:
                code = extract_code(llm(MUTATOR_MODEL, prompt))
                try:
                    s = run_candidate(code)
                except Timeout:
                    rescued = shrink_loops(code)
                    if rescued == code:
                        raise
                    print(f"gen {g} island {isl_i}: timeout, retrying with 1/10 loops")
                    code = rescued
                    s = run_candidate(code)
                if s is None:
                    print(f"gen {g} island {isl_i}: invalid matrix (shape/2-cycle/diagonal)")
                else:
                    add_entry(island, {'code': code, 'score': list(s), 'gen': g})
                    best = min(e['score'][0] for e in island)
                    print(f"gen {g} island {isl_i}: candidate {s[0]} (nsat {s[1]})  island best {best}")
                    if s[0] == 0:
                        print("!!!! COUNTEREXAMPLE-SCORING PROGRAM — verify independently !!!!")
                        open(f'SOLUTION_PROGRAM_gen{g}.py', 'w').write(code)
            except Exception as ex_:
                print(f"gen {g} island {isl_i}: candidate failed ({type(ex_).__name__}: {ex_})")
            island.sort(key=lambda e: e['score'][0])
            del island[POP_CAP:]
        if g % MIGRATE_EVERY == 0:               # ring migration of champions
            champs = [isl[0] for isl in db['islands'] if isl]
            for i, ch in enumerate(champs):
                add_entry(db['islands'][(i + 1) % ISLANDS], dict(ch))
            print(f"gen {g}: migration done")
        if g % ANALYZE_EVERY == 0:
            try:
                allbest = sorted((e for isl in db['islands'] for e in isl),
                                 key=lambda e: e['score'][0])[:5]
                summary = "\n".join(f"score {e['score']}: {e['code'][:400]}"
                                    for e in allbest)
                note = llm(ANALYST_MODEL,
                    f"{TASK}\n\nTop programs so far:\n{summary}\n\n"
                    "In <=150 words: what structural ideas are underexplored? "
                    "Give concrete next directions for the mutator.")
                db['notes'].append(note.strip())
                print(f"gen {g}: analyst note refreshed")
            except Exception as ex_:
                print(f"gen {g}: analyst call failed ({type(ex_).__name__}: {ex_})")
        entries = [e for isl in db['islands'] for e in isl]
        if entries:
            gb = min(entries, key=lambda e: e['score'][0])
            db.setdefault('history', []).append(
                [g, gb['score'][0], gb['score'][1]])   # gen, best total, best nsat
        db['gen'] = g
        save_db(db)
    entries = [e for isl in db['islands'] for e in isl]
    if entries:
        best = min(entries, key=lambda e: e['score'][0])
        print(f"done. global best score: {best['score'][0]} "
              f"(nsat {best['score'][1]}, gen {best['gen']})")

if __name__ == '__main__':
    main()
