"""Shared cost-matrix fixtures for the dense and sparse solver tests."""

import pytest

from test_utils import (
    get_dense_100x100_int, get_dense_100x100_int_hard,
    get_dense_1kx1k_int, get_dense_1kx1k_int_hard, get_dense_eps,
    get_sparse_100x100_int, get_sparse_1kx1k_int, get_sparse_4kx4k_int,
)


# Keep function scope: some tests modify their matrices in place.
@pytest.fixture
def dense_100x100_int():
    return get_dense_100x100_int()


@pytest.fixture
def dense_100x100_int_hard():
    return get_dense_100x100_int_hard()


@pytest.fixture
def sparse_100x100_int():
    return get_sparse_100x100_int()


@pytest.fixture
def dense_1kx1k_int():
    return get_dense_1kx1k_int()


@pytest.fixture
def dense_1kx1k_int_hard():
    return get_dense_1kx1k_int_hard()


@pytest.fixture
def sparse_1kx1k_int():
    return get_sparse_1kx1k_int()


@pytest.fixture
def sparse_4kx4k_int():
    return get_sparse_4kx4k_int()


@pytest.fixture
def dense_eps():
    return get_dense_eps()
