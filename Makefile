PY ?= python3

.PHONY: verify-all verify-hashes verify-t1 verify-t1p verify-o1 verify-t5 \
        verify-t2 verify-t2-full verify-t6 verify-t7-spec verify-t7 \
        verify-t8 verify-t9 verify-m1

verify-all:            ## all fast checks (seconds; t2/t6 use recorded logs)
	$(PY) verify/check_claims.py
	$(PY) verify/check_t7_from_spec.py
	$(PY) constructions/upper_bound_family.py --verify
	$(PY) verify/check_t8.py
	$(PY) verify/check_m1_high.py
	$(PY) verify/check_band.py
	$(PY) verify/check_m1.py

verify-hashes:         ## data/ graphs match manifest.json
	$(PY) verify/check_claims.py hashes

verify-t1:             ## pure m-ring: excess = m
	$(PY) verify/check_claims.py t1

verify-t1p:            ## C_m^k power ring: E(25)<=5, E(35)<=5, E(49)<=7
	$(PY) verify/check_claims.py t1p

verify-o1:             ## evolved champions: E(50)<=8 and <=5
	$(PY) verify/check_claims.py o1

verify-t5:             ## Pisa Conjecture 5.1 counterexamples
	$(PY) verify/check_claims.py t5

verify-t2:             ## n=17 lower bound: recorded CP-SAT log
	$(PY) verify/check_claims.py t2

verify-t2-full:        ## n=17 lower bound: re-prove from scratch (~4 min)
	$(PY) verify/check_claims.py t2-full

verify-t6:             ## GKZ Conj 8.2 k=3: live n<=9 + recorded scan
	$(PY) verify/check_claims.py t6

verify-t7-spec:        ## T7: rebuild the family from its spec, score with the independent verifier
	$(PY) verify/check_t7_from_spec.py

verify-t7:             ## T7: the family's own self-check, n=24..150, both variants, 3 implementations
	$(PY) constructions/upper_bound_family.py --verify

verify-t8:             ## T8: E(2k+1)=2k+1 spot-check (circulants k=4..8 + regular-tournament walk)
	$(PY) verify/check_t8.py

verify-t9:             ## T9: blow-up class, 4 independent checks of "excess<=3 forces 3|n" (~3.5 min)
	$(PY) blowup/verify_blowup_independent.py --check all

verify-m1:             ## M1: re-score the 77 measured witnesses in data/sonar_best/ (n=24..100)
	$(PY) verify/check_m1.py

verify-m1-high:        ## the 101..150 shortfall claim of note 5.2 (40 match, 10 above)
	$(PY) verify/check_m1_high.py

verify-d2core:         ## lib/dist2core: 3-implementation agreement + witness regression
	$(PY) lib/dist2core/tests/test_invariants.py
	$(PY) lib/dist2core/tests/test_regression.py

verify-d2core-t2:      ## lib/dist2core: re-prove E(17) >= 3 from a rebuilt model (~4 min)
	$(PY) lib/dist2core/tests/test_n17_infeasible.py

verify-blowup-calib:   ## blowup/: closed form vs family, stored witnesses, random cases
	$(PY) blowup/blowup_sweep.py --verify
	$(PY) blowup/blowup_inverse.py --test

verify-note-fresh:     ## the shipped note PDF was built from the shipped source
	$(PY) verify/check_note_fresh.py

verify-band:           ## upper bounds at 20..23, where the family G_n does not reach
	$(PY) verify/check_band.py
