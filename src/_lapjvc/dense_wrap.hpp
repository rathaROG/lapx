#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include <vector>
#include <cmath>
#include <limits>

#include "dense.hpp"

/**
	Updated on 2025/10/16 by rathaROG

    The return value is changed to include total_cost as the first element of the tuple.
    This is to avoid recalculating the total cost in Python, which can be inefficient for
    large matrices.
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
    T max_abs_cost = 0;
    for(int i = 0; i < nrows*ncols; ++i) {
        if (std::isfinite((double)data[i])) {
            any_finite = true;
            // Careful: Note that std::abs() is not a template.
            // https://en.cppreference.com/w/cpp/numeric/math/abs
            // https://en.cppreference.com/w/cpp/numeric/math/fabs
            max_abs_cost = std::max<T>(max_abs_cost, std::abs(data[i]));
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
    const T LARGE_COST = 2 * r * max_abs_cost + 1;
    std::vector<std::vector<T>> costs(n, std::vector<T>(n, LARGE_COST));

    for (int i = 0; i < nrows; i++)
    {
        T *cptr = data + i*ncols;
        for (int j = 0; j < ncols; j++)
        {
            const T c = cptr[j];
            if (std::isfinite((double)c))
                costs[i][j] = c;
        }
    }

    std::vector<int> Lmate, Rmate;
    solve_dense(costs, Lmate, Rmate);

    std::vector<int> rowids, colids;
    T total_cost = 0; // NEW: accumulate total assignment cost

    for (int i = 0; i < nrows; i++)
    {
        int mate = Lmate[i];
        if (Lmate[i] < ncols && costs[i][mate] != LARGE_COST)
        {
            rowids.push_back(i);
            colids.push_back(mate);
            total_cost += costs[i][mate]; // Sum up the cost for each assigned pair
        }
    }

    if (return_cost)
        return py::make_tuple(total_cost, py::array(rowids.size(), rowids.data()), py::array(colids.size(), colids.data()));
    else
        return py::make_tuple(py::array(rowids.size(), rowids.data()), py::array(colids.size(), colids.data()));

}