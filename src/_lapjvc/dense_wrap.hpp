#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include <vector>
#include <cmath>
#include <limits>
#include <type_traits>

#include "dense.hpp"

/**
    Updated by rathaROG:

    2025/10/30: Improve speed almost 2x for rectangular matrices by using ZERO padding
    for dummy rows/columns instead of LARGE_COST padding. This avoids filling the entire
    padded area with LARGE_COST and speeds up rectangular cases significantly.

    2025/10/16: The return value is changed to include total_cost as the first element of 
    the tuple. This is to avoid recalculating the total cost in Python, which can be 
    inefficient for large matrices.
*/

namespace py = pybind11;

template<typename T, int ExtraFlags>
py::tuple solve_dense_wrap(py::array_t<T, ExtraFlags> input1, bool return_cost = true) {
    auto buf1 = input1.request();

    if (buf1.ndim != 2)
        throw std::runtime_error("Number of dimensions must be two");

    const int nrows = int(buf1.shape[0]);
    const int ncols = int(buf1.shape[1]);

    if (nrows == 0 || ncols == 0) {
        if (return_cost)
            return py::make_tuple(T(0), py::array(), py::array());
        else
            return py::make_tuple(py::array(), py::array());
    }

    T *data = (T *)buf1.ptr;

    bool any_finite = false;
    double max_abs_cost_d = 0.0;
    for (int i = 0; i < nrows * ncols; ++i) {
        // We cast to double for the finiteness check. For integer T this is always finite.
        double dv = static_cast<double>(data[i]);
        if (std::isfinite(dv)) {
            any_finite = true;
            // Use fabs on double to avoid template pitfalls and integer overflow on abs(INT_MIN).
            max_abs_cost_d = std::max(max_abs_cost_d, std::fabs(dv));
        }
    }

    if (!any_finite) {
        if (return_cost)
            return py::make_tuple(T(0), py::array(), py::array());
        else
            return py::make_tuple(py::array(), py::array());
    }

    const int r = std::min<int>(nrows, ncols);
    const int n = std::max<int>(nrows, ncols);

    // Compute a LARGE_COST sentinel for forbidden entries within the original rectangle.
    // Use double to compute and clamp if T is integral to avoid overflow.
    double large_cost_d = 2.0 * static_cast<double>(r) * max_abs_cost_d + 1.0;
    T LARGE_COST;
    if constexpr (std::is_floating_point<T>::value) {
        LARGE_COST = static_cast<T>(large_cost_d);
    } else {
        // Clamp to a safe large value for integer types.
        using Lim = std::numeric_limits<T>;
        double cap = std::min<double>(static_cast<double>(Lim::max()) / 2.0, large_cost_d);
        LARGE_COST = static_cast<T>(cap);
    }

    // Build square cost matrix with ZERO padding for dummy rows/columns (fast for rectangular).
    // Only set LARGE_COST for forbidden entries inside the original MxN region.
    std::vector<std::vector<T>> costs(n, std::vector<T>(n, T(0)));

    for (int i = 0; i < nrows; ++i) {
        T *cptr = data + i * ncols;
        for (int j = 0; j < ncols; ++j) {
            const T c = cptr[j];
            // For floats: non-finite => forbidden. For integers: always finite => allowed.
            bool finite = std::isfinite(static_cast<double>(c));
            costs[i][j] = finite ? c : LARGE_COST;
        }
    }
    // Note:
    // - If nrows < ncols, rows [nrows..n-1] remain zero => dummy rows.
    // - If ncols < nrows, cols [ncols..n-1] remain zero => dummy columns.
    // This avoids filling the entire padded area with LARGE_COST and speeds up rectangular cases.

    std::vector<int> Lmate, Rmate;
    solve_dense(costs, Lmate, Rmate);

    std::vector<int> rowids, colids;
    T total_cost = T(0);

    // Collect only real (row, col) matches. Exclude dummy columns (j >= ncols) and forbidden.
    for (int i = 0; i < nrows; ++i) {
        int mate = Lmate[i];
        if (mate >= 0 && mate < ncols && costs[i][mate] != LARGE_COST) {
            rowids.push_back(i);
            colids.push_back(mate);
            total_cost = static_cast<T>(static_cast<double>(total_cost) + static_cast<double>(costs[i][mate]));
        }
    }

    if (return_cost)
        return py::make_tuple(total_cost,
                              py::array(rowids.size(), rowids.data()),
                              py::array(colids.size(), colids.data()));
    else
        return py::make_tuple(py::array(rowids.size(), rowids.data()),
                              py::array(colids.size(), colids.data()));
}