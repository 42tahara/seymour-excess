#!/usr/bin/env python3
"""Machine check that every graph in data/ matches the sha1 recorded in
data/manifest.json (and, where present, the file's own embedded sha1).

Canonical hash = sha1 of the sorted-key JSON adjacency dict
{"0": [j, ...], ...} — the same convention used throughout the project, so
hashes here are comparable with the README tables and the handoff records.

Usage: python3 check_hashes.py            # verify
       python3 check_hashes.py --write    # (re)generate manifest.json
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def _adj(obj):
    if isinstance(obj, list):                     # matrix -> adjacency dict
        return {i: [j for j in range(len(obj)) if obj[i][j]]
                for i in range(len(obj))}
    raw = obj.get("adj", obj)
    return {int(i): sorted(int(j) for j in nbrs) for i, nbrs in raw.items()}


def canonical_sha1(obj):
    """Manifest convention: int keys, numeric order (pisa_check/power_ring)."""
    return hashlib.sha1(
        json.dumps(_adj(obj), sort_keys=True).encode()).hexdigest()


def legacy_sha1(obj):
    """Champion-file convention: string keys, lexicographic order (evolve.py)."""
    adj = {str(i): v for i, v in _adj(obj).items()}
    return hashlib.sha1(
        json.dumps(adj, sort_keys=True).encode()).hexdigest()


def graph_files():
    for f in sorted(os.listdir(DATA)):
        if f.endswith(".json") and f != "manifest.json" \
                and f not in ("en_sweep.json", "pisa_results.json"):
            yield f


def main():
    path = os.path.join(DATA, "manifest.json")
    if "--write" in sys.argv:
        manifest = {f: canonical_sha1(json.load(open(os.path.join(DATA, f))))
                    for f in graph_files()}
        json.dump(manifest, open(path, "w"), indent=1)
        print(f"wrote {len(manifest)} entries to manifest.json")
        return
    manifest = json.load(open(path))
    bad = []
    for f, want in sorted(manifest.items()):
        obj = json.load(open(os.path.join(DATA, f)))
        got = canonical_sha1(obj)
        # champion files carry a code-lineage id in 'sha1' (see 'sha1_kind');
        # the graph hash lives in 'graph_sha1'.  Bare 'sha1' without a kind
        # marker is expected to be a graph hash in either key convention.
        embedded = None
        if isinstance(obj, dict):
            embedded = obj.get("graph_sha1") or \
                (obj.get("sha1") if "sha1_kind" not in obj else None)
        ok = got == want and (embedded is None
                              or embedded in (got, legacy_sha1(obj)))
        print(f"{'OK ' if ok else 'FAIL'} {f}  {got[:12]}")
        if not ok:
            bad.append(f)
    extra = [f for f in graph_files() if f not in manifest]
    if extra:
        print(f"WARNING: unmanifested graph files: {extra}")
        bad += extra
    if bad:
        sys.exit(f"FAIL: {bad}")
    print(f"PASS: {len(manifest)} graphs match manifest")


if __name__ == "__main__":
    main()
