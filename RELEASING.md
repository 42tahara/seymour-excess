# Release procedure (v0.1.0 and later)

Owner actions (requires the owner's GitHub and Zenodo accounts):

1. **Zenodo link (once):** log in at zenodo.org with GitHub → Settings →
   GitHub → flip the toggle ON for this repository.
2. **Release:** `git tag v0.1.0 && git push --tags`, then on GitHub draft a
   release from the tag. Zenodo archives it automatically and mints a DOI
   within minutes.
3. **Write back:** paste the DOI (use the *concept DOI* so it covers future
   versions) into README "Cite as", commit.

Pre-release checklist:

- [ ] repository name finalised (owner)
- [ ] author line + copyright holder in README/LICENSE finalised (owner)
- [ ] supervisor's note PDF merged into note/
- [ ] `make verify-all` green on a fresh clone
- [ ] no secrets: `git grep -I "sk-ant"` empty; no evolve_db/raw logs tracked
- [ ] in-progress tables updated (desert probes, GKZ 8.2 scan range, δ=8)
