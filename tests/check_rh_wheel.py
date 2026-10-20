# Copyright (c) 2026 Ratha SIV | MIT License
"""Standalone installed-wheel check; only NumPy is required."""
import argparse
import ast
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path

import lap
import numpy as np


def check_typing_exports(expect_rh):
    init = Path(lap.__file__)
    for module, names in (('_lapjv', ('lapjv',)),
                          ('_lapjvx', ('lapjvx', 'lapjvxa')),
                          ('_lapjvc', ('lapjvc',))):
        assert init.with_name(module + '.pyi').is_file(), 'Missing native solver stub: ' + module
        assert not init.with_name(module + '_wp.py').exists(), 'Wheel contains a former forwarding wrapper'
        for name in names:
            assert getattr(lap, name) is getattr(import_module('lap.' + module), name), name
    assert init.with_name('_lapjv_rh.pyi').is_file() == expect_rh, 'Unexpected R/H stub presence'
    assert not init.with_name('_lapjvr.pyi').exists(), 'Wheel contains the former R/H stub'
    assert find_spec('lap._lapjvr') is None, 'Wheel contains the former R/H extension'
    imports_rh = any(isinstance(node, ast.ImportFrom) and node.module == '_lapjv_rh'
                     for node in ast.walk(ast.parse(init.read_text(encoding='utf-8'))))
    assert imports_rh == expect_rh, 'Typing exports do not match the compiled families'


def check_legacy_only():
    check_typing_exports(expect_rh=False)
    names = ('lapjvr', 'lapjvh', 'lapjvr_batch', 'lapjvh_batch')
    assert find_spec('lap._lapjv_rh') is None, 'Legacy-only wheel contains the R/H extension'
    for name in names:
        assert name not in lap.__all__ and not hasattr(lap, name), 'Unexpected export: ' + name

    costs = np.array([[3., 1.], [1., 4.]], dtype=np.float64)
    for name in ('lapjv', 'lapjvx', 'lapjvxa', 'lapjvc', 'lapjvs', 'lapjvsa'):
        assert name in lap.__all__, 'Wheel is missing ' + name
        result = getattr(lap, name)(costs)
        assert result[0] == 2, name
        if name == 'lapjv':
            np.testing.assert_array_equal(result[1], [1, 0])
            np.testing.assert_array_equal(result[2], [1, 0])
        elif name.endswith('a'):
            np.testing.assert_array_equal(result[1], [[0, 1], [1, 0]])
        else:
            np.testing.assert_array_equal(result[1], [0, 1])
            np.testing.assert_array_equal(result[2], [1, 0])

    batch = np.stack([costs] * 3)
    for name in ('lapjvx_batch', 'lapjvxa_batch', 'lapjvs_batch', 'lapjvsa_batch'):
        assert name in lap.__all__, 'Wheel is missing ' + name
        result = getattr(lap, name)(batch, n_threads=2)
        np.testing.assert_array_equal(result[0], [2, 2, 2])
        for index in range(3):
            if name in ('lapjvxa_batch', 'lapjvsa_batch'):
                np.testing.assert_array_equal(result[1][index], [[0, 1], [1, 0]])
            else:
                np.testing.assert_array_equal(result[1][index], [0, 1])
                np.testing.assert_array_equal(result[2][index], [1, 0])

    sparse = (2, costs.ravel(), np.array([0, 2, 4], dtype=np.int32),
              np.array([0, 1, 0, 1], dtype=np.int32))
    assert 'lapmod' in lap.__all__ and 'lapmod_batch' in lap.__all__
    total, x, y = lap.lapmod(*sparse)
    assert total == 2
    np.testing.assert_array_equal(x, [1, 0])
    np.testing.assert_array_equal(y, [1, 0])
    totals, xs, ys = lap.lapmod_batch([sparse] * 3, n_threads=2)
    np.testing.assert_array_equal(totals, [2, 2, 2])
    for x, y in zip(xs, ys):
        np.testing.assert_array_equal(x, [1, 0])
        np.testing.assert_array_equal(y, [1, 0])
    print('All pre-existing solvers are available; R/H families omitted:', lap.__file__)


def check_rh():
    check_typing_exports(expect_rh=True)
    costs = np.array([[3., 1., 8.], [1., 4., 7.]], dtype=np.float32)
    repeated = np.random.default_rng(20261019).random((96, 96))
    repeated[:70] = repeated[0]
    for name in ('lapjvr', 'lapjvh'):
        assert name in lap.__all__, 'Wheel is missing ' + name
        solve = getattr(lap, name)
        batch_solve = getattr(lap, name + '_batch')
        total, pairs = solve(costs, extend_cost=True, output='pairs')
        assert total == 2 and pairs.dtype == np.int64
        np.testing.assert_array_equal(pairs, [[0, 1], [1, 0]])
        # Squares select the family's completion; rectangles share the Rust path.
        for matrix in (costs, costs[:, :2], costs.T, repeated):
            batch = np.stack([matrix] * 3)
            actual = batch_solve(batch, extend_cost=True, output='pairs',
                                 return_cost=False, n_threads=2)
            wanted = solve(matrix, extend_cost=True, output='pairs', return_cost=False)
            for result in actual:
                np.testing.assert_array_equal(result, wanted)
            np.testing.assert_array_equal(
                wanted, lap.lapjvr(matrix, extend_cost=True, output='pairs', return_cost=False))
    print('Both LAPJVR and LAPJVH are available:', lap.__file__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-only', action='store_true',
                        help='require every pre-existing solver and no R/H extension')
    args = parser.parse_args()
    if args.legacy_only:
        check_legacy_only()
    else:
        check_rh()
