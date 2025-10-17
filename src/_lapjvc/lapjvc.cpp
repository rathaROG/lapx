#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "dense_wrap.hpp"

namespace py = pybind11;

void register_lapjvc(py::module_& m) {
    m.def(
        "lapjvc",
        &solve_dense_wrap<int32_t, py::array::c_style>,
        py::arg("costs").noconvert(),
        py::arg("return_cost") = true,
        R"pbdoc(
Solve the Linear Assignment Problem using the classic dense Jonker-Volgenant algorithm (O(n³)).

This function computes the optimal assignment for a given cost matrix using the classic shortest augmenting path
algorithm described by Jonker & Volgenant (1987). This is the "dense" version (also known as the classic JV algorithm),
not the modern sparse-optimized LAPJV.

Features:
- Handles both square and rectangular cost matrices (internally pads with large costs as needed).
- NaN entries in the cost matrix are treated as forbidden assignments.
- Supports multiple data types: int32, int64, float32, float64.

Args:
    costs (numpy.ndarray): 2D cost matrix (MxN), convertible to float64, float32, int32, or int64.
    return_cost (bool): If True (default), return (total_cost, row_indices, col_indices).
                        If False, return only (row_indices, col_indices).

Returns:
    tuple: (total_cost, row_indices, col_indices), or (row_indices, col_indices) if return_cost=False.

Example:
    >>> import numpy as np
    >>> import lap
    >>> costs = np.array([[6, 9, 1], [10, 3, 2], [8, 7, 4.]], dtype=np.float32)
    >>> total_cost, rids, cids = lap.lapjvc(costs)
    >>> print(list(zip(rids, cids)))
    [(0, 2), (1, 1), (2, 0)]

Notes:
    - This is the classic O(n³) dense Jonker-Volgenant algorithm, ideal for only square cost matrices.
    - For large, sparse, or rectangular problems, consider lapjv() or lapjvx() for better performance.
    - Forbidden assignments can be specified with np.nan (float types).

References:
    - Jonker, R., & Volgenant, A. (1987). "A shortest augmenting path algorithm for dense and sparse linear assignment problems." Computing, 38(4), 325–340.
    - Code adapted and vendored from py-lapsolver (MIT License) by Christoph Heindl, based on Jaehyun Park's MinCostMatching.cc.

)pbdoc"
    );
    m.def(
        "lapjvc",
        &solve_dense_wrap<int64_t, py::array::c_style>,
        py::arg("costs").noconvert(),
        py::arg("return_cost") = true
    );
    m.def(
        "lapjvc",
        &solve_dense_wrap<float, py::array::c_style>,
        py::arg("costs").noconvert(),
        py::arg("return_cost") = true
    );
    m.def(
        "lapjvc",
        &solve_dense_wrap<double, py::array::c_style>,
        py::arg("costs"),
        py::arg("return_cost") = true
    );
}

PYBIND11_MODULE(_lapjvc, m) {
    register_lapjvc(m);
}
