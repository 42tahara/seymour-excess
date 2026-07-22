PY ?= python3

.PHONY: verify-all verify-hashes verify-t1 verify-t1p verify-o1 verify-t5 \
        verify-t2 verify-t2-full verify-t6

verify-all:            ## all fast checks (seconds; t2/t6 use recorded logs)
	$(PY) verify/check_claims.py

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
