#!/usr/bin/env python3
"""Check that the shipped note PDF was built from the shipped note source.

Run from the repository root:  python3 verify/check_note_fresh.py

Why this exists.  Editing measuring-the-moat.tex and forgetting to rebuild
leaves a repository whose source says one thing and whose PDF -- the artefact
a reader actually opens -- says another.  That happened during the assembly of
v2.0: three wording fixes went into the source and the committed PDF kept the
old sentences.  A checklist item asking a human to remember does not catch it;
this does.

Method: rebuild the note from the shipped source in a temporary directory and
compare the extracted text with the text of the shipped PDF.  Timestamps and
producer metadata differ between builds, so the comparison is on text, not on
bytes.  Requires `tectonic` and `pdftotext`; if either is missing the check
reports that and exits 0, since it is then not a failure of the repository.
"""
import os
import shutil
import subprocess
import sys
import tempfile

SRC = 'note/measuring-the-moat.tex'
PDF = 'note/measuring-the-moat-v2.1.pdf'
DEPS = ('note/refs.bib', 'note/table_generated.tex')


def text_of(pdf):
    out = subprocess.run(['pdftotext', pdf, '-'],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"FAIL: pdftotext failed on {pdf}")
    # Collapse whitespace: line breaking is not stable across builds.
    return ' '.join(out.stdout.split())


for tool in ('tectonic', 'pdftotext'):
    if shutil.which(tool) is None:
        print(f"SKIP: {tool} not installed; cannot check that {PDF} is current")
        sys.exit(0)

for f in (SRC, PDF) + DEPS:
    if not os.path.exists(f):
        sys.exit(f"FAIL: {f} missing")

with tempfile.TemporaryDirectory() as tmp:
    for f in (SRC,) + DEPS:
        shutil.copy(f, tmp)
    build = subprocess.run(
        ['tectonic', '-X', 'compile', os.path.basename(SRC)],
        cwd=tmp, capture_output=True, text=True)
    if build.returncode != 0:
        sys.exit("FAIL: the note does not build from its own source\n"
                 + build.stderr[-2000:])
    rebuilt = os.path.join(tmp, os.path.basename(SRC).replace('.tex', '.pdf'))
    fresh, shipped = text_of(rebuilt), text_of(PDF)

if fresh == shipped:
    print(f"PASS: {PDF} matches a fresh build of {SRC} "
          f"({len(shipped)} characters of text)")
    sys.exit(0)

# Report where they diverge, in words rather than characters.
a, b = fresh.split(), shipped.split()
i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]),
         min(len(a), len(b)))
print(f"FAIL: {PDF} was not built from the current {SRC}")
print(f"  first difference at word {i} of {len(b)} (shipped) / {len(a)} (fresh)")
print(f"  shipped: ...{' '.join(b[max(0, i-12):i+12])}...")
print(f"  fresh  : ...{' '.join(a[max(0, i-12):i+12])}...")
print("  rebuild with: tectonic -X compile note/measuring-the-moat.tex")
sys.exit(1)
