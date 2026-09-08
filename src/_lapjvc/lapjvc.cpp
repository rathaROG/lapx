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
Solve the linear assignment problem with the classic dense Jonker-Volgenant algorithm (O(n³)).

This function calculates an optimal assignment for a cost matrix.
It uses the shortest augmenting path algorithm from Jonker and Volgenant (1987).
This is the dense version, also called the classic JV algorithm.
It differs from the modern LAPJV version optimized for sparse matrices.

Features:
- The solver accepts square and rectangular cost matrices. It pads with large costs when necessary.
- The solver treats NaN entries as forbidden assignments.
- The solver supports int32, int64, float32, and float64.

Args:
    costs (numpy.ndarray): A 2D cost matrix with shape (M, N).
                          It must permit conversion to float64, float32, int32, or int64.
    return_cost (bool): If True (default), return (total_cost, row_indices, col_indices).
                       If False, return (row_indices, col_indices).

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
    - The classic O(n³) dense Jonker-Volgenant algorithm is best suited to square cost matrices.
    - For large, sparse, or rectangular problems, consider lapjv() or lapjvx() for better performance.
    - Use np.nan to represent forbidden assignments in floating inputs.

References:
    - Jonker, R., & Volgenant, A. (1987). "A shortest augmenting path algorithm for dense and sparse linear assignment problems." Computing, 38(4), 325–340.
    - This code adapts and includes Christoph Heindl's py-lapsolver (MIT License).
      That project uses Jaehyun Park's MinCostMatching.cc as its basis.

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
