#ifndef LAPJVR_H
#define LAPJVR_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
int lapjvr_run(const void *costs, int cost32, const void *original,
    int original32, size_t batch, size_t rows, size_t cols, double limit,
    size_t threads, int automatic, int pairs, int return_cost, int hybrid, int64_t *output,
    size_t *counts, double *totals, size_t *error_index);
#ifdef __cplusplus
}
#endif
#endif
