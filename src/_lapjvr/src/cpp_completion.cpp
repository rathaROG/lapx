// Copyright (c) 2016 Vadim Markovtsev (source{d})
// Copyright (c) 2026 Ratha SIV
// The JVS-derived LAPJVR completion, expressed in C++. MIT; see ../LICENSE.
// This optional kernel preserves the Rust completion algorithm and operation order.
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>

template<class Cost, bool Profile>
static int augment(const Cost* __restrict costs, std::size_t n, std::size_t count,
                   std::size_t* __restrict x, std::size_t* __restrict y,
                   std::size_t* __restrict columns, const std::size_t* __restrict free_rows,
                   std::size_t* __restrict pred, double* __restrict d,
                   double* __restrict v, std::uint64_t* counters) noexcept {
    constexpr auto free = std::numeric_limits<std::size_t>::max();
    for (std::size_t f = 0; f < count; ++f) {
        const auto root = free_rows[f];
        if (root >= n) return 2;
        if constexpr (Profile) ++counters[0];
        for (std::size_t j = 0; j < n; ++j) {
            d[j] = static_cast<double>(costs[root*n+j]) - v[j];
            pred[j] = root;
            columns[j] = j;
        }
        std::size_t low = 0, up = 0, scanned = 0, end = free;
        double minimum = 0;
        while (end == free) {
            if (up == low) {
                scanned = low;
                if (up == n) return 1;
                minimum = d[columns[up++]];
                const auto start = up;
                if constexpr (Profile) counters[1] += n-start;
                for (auto k = start; k < n; ++k) {
                    const auto j = columns[k];
                    const double h = d[j];
                    if (h <= minimum) {
                        if (h < minimum) {
                            up = low;
                            minimum = h;
                        }
                        columns[k] = columns[up];
                        columns[up++] = j;
                    }
                }
                if (!std::isfinite(minimum)) return 1;
                for (auto k = low; k < up; ++k) {
                    if (y[columns[k]] == free) {
                        end = columns[k];
                        break;
                    }
                }
                if (end != free) break;
            }
            const auto j1 = columns[low++];
            const auto i = y[j1];
            if (i >= n) return 2;
            const auto* row = costs+i*n;
            const double h = static_cast<double>(row[j1]) - v[j1] - minimum;
            const auto start = up;
            if constexpr (Profile) counters[2] += n-start;
            for (auto k = start; k < n; ++k) {
                const auto j = columns[k];
                const double candidate = static_cast<double>(row[j]) - v[j] - h;
                if (candidate < d[j]) {
                    pred[j] = i;
                    if (candidate == minimum) {
                        if (y[j] == free) {
                            if constexpr (Profile) counters[2] -= n-k-1;
                            end = j;
                            break;
                        }
                        columns[k] = columns[up];
                        columns[up++] = j;
                    }
                    d[j] = candidate;
                }
            }
        }
        for (std::size_t k = 0; k < scanned; ++k) {
            const auto j = columns[k];
            v[j] = v[j] + d[j] - minimum;
        }
        auto j = end;
        for (std::size_t steps = 0; steps < n; ++steps) {
            const auto i = pred[j];
            if (i >= n) return 2;
            y[j] = i;
            const auto previous = x[i];
            x[i] = j;
            if (i == root) break;
            if (previous >= n) return 2;
            j = previous;
        }
    }
    return 0;
}

extern "C" int lapjvr_hybrid_augment(
    const void* costs, int float32, std::size_t n, std::size_t count,
    std::size_t* x, std::size_t* y, std::size_t* columns, const std::size_t* free_rows,
    std::size_t* pred, double* d, double* v, std::uint64_t* counters) noexcept {
    if (float32) {
        const auto* values = static_cast<const float*>(costs);
        return counters ? augment<float, true>(values,n,count,x,y,columns,free_rows,pred,d,v,counters)
                        : augment<float, false>(values,n,count,x,y,columns,free_rows,pred,d,v,nullptr);
    }
    const auto* values = static_cast<const double*>(costs);
    return counters ? augment<double, true>(values,n,count,x,y,columns,free_rows,pred,d,v,counters)
                    : augment<double, false>(values,n,count,x,y,columns,free_rows,pred,d,v,nullptr);
}
