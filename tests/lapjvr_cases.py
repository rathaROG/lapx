# Copyright (c) 2026 Ratha SIV | MIT License
"""Preserved tracking and finite-limit fixtures for LAPJVR tests.

Every family is independently seeded. Row/column permutations prevent the
affordability sample from relying on contiguous blocks. Generation is untimed.
"""

import hashlib

import numpy as np


def conflict_cases(seed=20261031, dtype='float64', sizes=None):
    cases = []
    families = ('shuffled', 'mild', 'overlap', 'three', 'tied', 'negative',
                'balanced', 'bridged', 'uniform', 'constant')
    for n in sizes if sizes is not None else (50, 250):
        for family in families:
            for batch in (False, True):
                name = f"dense-{'batch-' if batch else ''}{family}-{n}x{n}"
                rng = np.random.default_rng(int.from_bytes(
                    hashlib.sha256(f'{seed}:{name}'.encode()).digest()[:8], 'little'))
                limit = -.5 if family == 'negative' else .5
                costs = rng.random((8 if n >= 128 else 16, n, n) if batch else (n, n)) + limit + .1
                for a in costs if batch else costs[None]:
                    def block(r0, r1, c0, c1):
                        a[r0:r1, c0:c1] = limit - .3 - .2*rng.random((r1-r0,c1-c0))
                    k, c = 3*n//4, n//4
                    if family == 'mild':
                        k, c = 5*n//8, 3*n//8
                    if family in ('uniform', 'constant'):
                        a[:] = rng.random((n,n)) if family == 'uniform' else .125
                    elif family == 'three':
                        block(0,n//2,0,n//8)
                        block(n//2,3*n//4,n//8,n//2)
                        block(3*n//4,n,n//2,n)
                    elif family == 'balanced':
                        for lo,hi in ((0,n//4),(n//4,n//2),(n//2,n)):
                            block(lo,hi,lo,hi)
                    else:
                        block(0,k,0,c)
                        block(k,n,0 if family == 'overlap' else c,n)
                        if family == 'bridged':
                            # Affordable bridges complete the graph, while the
                            # cheap neighborhoods remain highly congested.
                            a[a >= limit] = limit-.01
                        elif family == 'tied':
                            a[a < limit] = .125
                    a[:] = a[rng.permutation(n)][:,rng.permutation(n)]
                cases.append((name,costs.astype(dtype),batch,limit))
    return cases

def tracking_costs(n, m, seed, dtype):
    """Same synthetic cost generator as the historical fastlap harness.

    These new cases time public solver calls only, without tracking decoration.
    """
    rng = np.random.default_rng(seed)
    centers = rng.uniform(0, 1000, (n, 2))
    sizes = rng.uniform(25, 100, (n, 2))
    common = max(1, int(min(n, m) * .75))
    detection_centers = rng.uniform(0, 1000, (m, 2))
    detection_sizes = rng.uniform(25, 100, (m, 2))
    detection_centers[:common] = centers[:common] + rng.normal(0, 12, (common, 2))
    detection_sizes[:common] = sizes[:common] * rng.uniform(.8, 1.2, (common, 2))
    order = rng.permutation(m)
    detection_centers, detection_sizes = detection_centers[order], detection_sizes[order]
    lo = np.maximum((centers - sizes / 2)[:, None], detection_centers - detection_sizes / 2)
    hi = np.minimum((centers + sizes / 2)[:, None], detection_centers + detection_sizes / 2)
    intersection = np.maximum(hi - lo, 0).prod(axis=2)
    union = sizes.prod(axis=1)[:, None] + detection_sizes.prod(axis=1) - intersection
    appearance = rng.uniform(.4, 1, (n, m))
    inverse = np.argsort(order)
    appearance[np.arange(common), inverse[:common]] = rng.uniform(0, .15, common)
    return np.ascontiguousarray(.8 * (1 - intersection / union) + .2 * appearance, dtype=dtype)
