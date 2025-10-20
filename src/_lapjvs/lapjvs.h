#include <cassert>
#include <cstdio>
#include <limits>
#include <memory>

#ifdef __GNUC__
#define always_inline __attribute__((always_inline)) inline
#define restrict __restrict__
#elif _WIN32
#define always_inline __forceinline
#define restrict __restrict
#else
#define always_inline inline
#define restrict
#endif

template <typename idx, typename cost>
always_inline std::tuple<cost, cost, idx, idx>
find_umins_regular(
    idx dim, idx i, const cost *restrict assign_cost,
    const cost *restrict v) {
  const cost *local_cost = &assign_cost[i * dim];
  cost umin = local_cost[0] - v[0];
  idx j1 = 0;
  idx j2 = -1;
  cost usubmin = std::numeric_limits<cost>::max();
  for (idx j = 1; j < dim; j++) {
    cost h = local_cost[j] - v[j];
    if (h < usubmin) {
      if (h >= umin) {
        usubmin = h;
        j2 = j;
      } else {
        usubmin = umin;
        umin = h;
        j2 = j1;
        j1 = j;
      }
    }
  }
  return std::make_tuple(umin, usubmin, j1, j2);
}

template <typename idx, typename cost>
always_inline std::tuple<cost, cost, idx, idx>
find_umins(
    idx dim, idx i, const cost *restrict assign_cost,
    const cost *restrict v) {
  return find_umins_regular(dim, i, assign_cost, v);
}

/// @brief Exact Jonker-Volgenant algorithm (scalar-only).
/// @param dim in problem size
/// @param assign_cost in cost matrix
/// @param verbose in indicates whether to report the progress to stdout
/// @param rowsol out column assigned to row in solution / size dim
/// @param colsol out row assigned to column in solution / size dim
/// @param u out dual variables, row reduction numbers / size dim
/// @param v out dual variables, column reduction numbers / size dim
/// @return achieved minimum assignment cost
template <bool verbose, typename idx, typename cost>
cost lapjvs(int dim, const cost *restrict assign_cost, idx *restrict rowsol, 
    idx *restrict colsol, cost *restrict u, cost *restrict v) {
  auto collist = std::make_unique<idx[]>(dim);  // list of columns to be scanned in various ways.
  auto matches = std::make_unique<idx[]>(dim);  // counts how many times a row could be assigned.
  auto d = std::make_unique<cost[]>(dim);       // 'cost-distance' in augmenting path calculation.
  auto pred = std::make_unique<idx[]>(dim);     // row-predecessor of column in augmenting/alternating path.

  // init how many times a row will be assigned in the column reduction.
  for (idx i = 0; i < dim; i++) {
    matches[i] = 0;
  }

  // COLUMN REDUCTION
  for (idx j = dim - 1; j >= 0; j--) {  // reverse order gives better results.
    // find minimum cost over rows.
    cost min = assign_cost[j];
    idx imin = 0;
    for (idx i = 1; i < dim; i++) {
      const cost *local_cost = &assign_cost[i * dim];
      if (local_cost[j] < min) {
        min = local_cost[j];
        imin = i;
      }
    }
    v[j] = min;

    if (++matches[imin] == 1) {
      // init assignment if minimum row assigned for first time.
      rowsol[imin] = j;
      colsol[j] = imin;
    } else {
      colsol[j] = -1;  // row already assigned, column not assigned.
    }
  }
  if (verbose) {
    printf("lapjvs: COLUMN REDUCTION finished\n");
  }

  // REDUCTION TRANSFER
  auto free = matches.get();  // list of unassigned rows.
  idx numfree = 0;
  for (idx i = 0; i < dim; i++) {
    const cost *local_cost = &assign_cost[i * dim];
    if (matches[i] == 0) {  // fill list of unassigned 'free' rows.
      free[numfree++] = i;
    } else if (matches[i] == 1) {  // transfer reduction from rows that are assigned once.
      idx j1 = rowsol[i];
      cost min = std::numeric_limits<cost>::max();
      for (idx j = 0; j < dim; j++) {
        if (j != j1) {
          if (local_cost[j] - v[j] < min) {
            min = local_cost[j] - v[j];
          }
        }
      }
      v[j1] = v[j1] - min;
    }
  }
  if (verbose) {
    printf("lapjvs: REDUCTION TRANSFER finished\n");
  }

  // AUGMENTING ROW REDUCTION
  for (int loopcnt = 0; loopcnt < 2; loopcnt++) {  // loop to be done twice.
    idx k = 0;
    idx prevnumfree = numfree;
    numfree = 0;  // start list of rows still free after augmenting row reduction.
    while (k < prevnumfree) {
      idx i = free[k++];

      // find minimum and second minimum reduced cost over columns.
      cost umin, usubmin;
      idx j1, j2;
      std::tie(umin, usubmin, j1, j2) = find_umins(dim, i, assign_cost, v);

      idx i0 = colsol[j1];
      cost vj1_new = v[j1] - (usubmin - umin);
      bool vj1_lowers = vj1_new < v[j1];  // the trick to eliminate the epsilon bug
      if (vj1_lowers) {
        v[j1] = vj1_new;
      } else if (i0 >= 0) {  // minimum and subminimum equal.
        j1 = j2;
        i0 = colsol[j2];
      }

      rowsol[i] = j1;
      colsol[j1] = i;

      if (i0 >= 0) {
        if (vj1_lowers) {
          free[--k] = i0;
        } else {
          free[numfree++] = i0;
        }
      }
    }
    if (verbose) {
      printf("lapjvs: AUGMENTING ROW REDUCTION %d / %d\n", loopcnt + 1, 2);
    }
  }

  // AUGMENT SOLUTION for each free row.
  for (idx f = 0; f < numfree; f++) {
    idx endofpath;
    idx freerow = free[f];  // start row of augmenting path.
    if (verbose) {
      printf("lapjvs: AUGMENT SOLUTION row %d [%d / %d]\n",
             freerow, f + 1, numfree);
    }

    // Dijkstra shortest path algorithm.
    for (idx j = 0; j < dim; j++) {
      d[j] = assign_cost[freerow * dim + j] - v[j];
      pred[j] = freerow;
      collist[j] = j;
    }

    idx low = 0;
    idx up = 0;
    bool unassigned_found = false;
    idx last = 0;
    cost min = 0;
    do {
      if (up == low) {
        last = low - 1;
        min = d[collist[up++]];
        for (idx k = up; k < dim; k++) {
          idx j = collist[k];
          cost h = d[j];
          if (h <= min) {
            if (h < min) {
              up = low;
              min = h;
            }
            collist[k] = collist[up];
            collist[up++] = j;
          }
        }
        for (idx k = low; k < up; k++) {
          if (colsol[collist[k]] < 0) {
            endofpath = collist[k];
            unassigned_found = true;
            break;
          }
        }
      }

      if (!unassigned_found) {
        idx j1 = collist[low];
        low++;
        idx i = colsol[j1];
        const cost *local_cost = &assign_cost[i * dim];
        cost h = local_cost[j1] - v[j1] - min;
        for (idx k = up; k < dim; k++) {
          idx j = collist[k];
          cost v2 = local_cost[j] - v[j] - h;
          if (v2 < d[j]) {
            pred[j] = i;
            if (v2 == min) {
              if (colsol[j] < 0) {
                endofpath = j;
                unassigned_found = true;
                break;
              } else {
                collist[k] = collist[up];
                collist[up++] = j;
              }
            }
            d[j] = v2;
          }
        }
      }
    } while (!unassigned_found);

    for (idx k = 0; k <= last; k++) {
      idx j1 = collist[k];
      v[j1] = v[j1] + d[j1] - min;
    }

    {
      idx i;
      do {
        i = pred[endofpath];
        colsol[endofpath] = i;
        idx j1 = endofpath;
        endofpath = rowsol[i];
        rowsol[i] = j1;
      } while (i != freerow);
    }
  }
  if (verbose) {
    printf("lapjvs: AUGMENT SOLUTION finished\n");
  }

  // calculate optimal cost.
  cost lapcost = 0;
  for (idx i = 0; i < dim; i++) {
    const cost *local_cost = &assign_cost[i * dim];
    idx j = rowsol[i];
    u[i] = local_cost[j] - v[j];
    lapcost += local_cost[j];
  }
  if (verbose) {
    printf("lapjvs: optimal cost calculated\n");
  }

  return lapcost;
}