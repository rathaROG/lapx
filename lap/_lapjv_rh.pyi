# Copyright (c) 2026 Ratha SIV | MIT License

"""Static signatures and documentation for the native Rust and hybrid entry points."""

from typing import Any, List, Optional, Tuple, Union, overload
from typing_extensions import Literal, Protocol
import numpy as np

_Precision = Literal["native", "float32", "float64"]
_Output = Literal["indices", "pairs"]

class _SingleSolver(Protocol):
    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: Literal[True] = True,
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[float, np.ndarray, np.ndarray]: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        *,
        return_cost: Literal[False],
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[np.ndarray, np.ndarray]: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: bool = True,
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: Literal[True] = True,
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> Tuple[float, np.ndarray]: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> np.ndarray: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        *,
        return_cost: Literal[False],
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> np.ndarray: ...

    @overload
    def __call__(
        self, cost: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: bool = True,
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> Union[Tuple[float, np.ndarray], np.ndarray]: ...

    @overload
    def __call__(
        self, cost: Any, extend_cost: bool = False,
        cost_limit: float = ..., return_cost: bool = True,
        *, precision: _Precision = "native", output: _Output = "indices",
    ) -> Union[Tuple[float, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], Tuple[float, np.ndarray], np.ndarray]: ...

class _BatchSolver(Protocol):
    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["indices"] = "indices",
    ) -> Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: Literal[True] = True,
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> Tuple[np.ndarray, List[np.ndarray]]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool,
        cost_limit: float,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> List[np.ndarray]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        *,
        return_cost: Literal[False],
        n_threads: Optional[int] = 0,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> List[np.ndarray]: ...

    @overload
    def __call__(
        self, costs: Any,
        extend_cost: bool = False,
        cost_limit: float = ...,
        return_cost: bool = True,
        n_threads: Optional[int] = 0,
        *,
        precision: _Precision = "native",
        output: Literal["pairs"],
    ) -> Union[Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]: ...

    @overload
    def __call__(
        self, costs: Any, extend_cost: bool = False,
        cost_limit: float = ..., return_cost: bool = True,
        n_threads: Optional[int] = 0,
        *, precision: _Precision = "native", output: _Output = "indices",
    ) -> Union[Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]], Tuple[np.ndarray, List[np.ndarray]], List[np.ndarray]]: ...

lapjvr: _SingleSolver
"""Solve a cost matrix with the Rust Jonker-Volgenant solver.

Return aligned row and column indices or assignment pairs. When
return_cost=True, prepend the total cost of the selected matches.

Parameters
----------
cost : array_like, shape (N, M)
    Real numeric assignment costs. With precision='native', float32 and
    float64 inputs retain their cost precision. Other real numeric dtypes
    are normalized to float64.
    Positive infinity forbids an edge. Exclude NaN and negative infinity
    before calling; the solver does not check for these invalid values.
extend_cost : bool, default False
    Permit a rectangular matrix when cost_limit is infinite. Rectangular
    problems use a native path without padding to a square matrix. A finite
    cost_limit permits rectangular inputs regardless of this option.
cost_limit : float, default np.inf
    A finite limit permits unmatched rows and columns, each charged half
    the limit during optimization. The returned total excludes these
    penalties. Negative finite limits are allowed. With np.inf, require
    min(N, M) matches. NaN and negative infinity are invalid limits.
return_cost : bool, default True
    Prepend the total assignment cost if True. The total is accumulated in
    float64 from the selected input costs before any float32 downcast.
    False returns only indices or pairs and skips the total-cost sum.
precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
    Select the working cost precision. 'native' preserves float32/float64
    inputs and uses float64 for other real numeric inputs. Explicit
    'float32' or 'float64' converts the working costs. Finite costs and
    limits must fit the selected float32 range when float32 is used.
output : {'indices', 'pairs'}, keyword-only, default 'indices'
    'indices' returns aligned row and column arrays. 'pairs' returns a
    two-column array whose rows contain (row_index, column_index).

Returns
-------
total_cost : float, optional
    Present first only when return_cost=True. Sum of selected original
    costs, excluding unmatched penalties, even for finite cost_limit.
rows, cols : np.ndarray, shape (K,), dtype int64
    Returned when output='indices'. rows[i] is matched to cols[i]. Rows are
    sorted in increasing order; indices refer to the original matrix.
pairs : np.ndarray, shape (K, 2), dtype int64
    Returned instead of rows and cols when output='pairs'. K is at most
    min(N, M); finite limits can choose fewer matches. An empty dimension
    returns empty indices or pairs of shape (0, 2), with total 0.0.

Raises
------
TypeError
    cost has a non-real numeric dtype, such as complex, object, or string.
ValueError
    The input is not 2D, a nonempty rectangle is disallowed, an option or
    limit is invalid, float32 conversion overflows, dimensions exceed
    native limits, required matches are infeasible, or reduced costs
    overflow.
MemoryError
    An input copy, output array, or native workspace cannot be allocated.
RuntimeError
    An internal native solver error occurs.

Notes
-----
LAPJVR uses Rust for required square completion. Rectangular and
finite-limit problems use native Rust paths without square padding.

Required square problems use float64 search state even with float32 costs.
Rectangular and finite-limit paths use the selected working precision.
A finite limit optimizes rejection jointly with matching; it is not
equivalent to filtering a required solution after solving. Equal-cost
optima can produce different assignments across solvers or precisions.

Suitable contiguous arrays are borrowed and the native solve releases the
GIL. Other inputs may be copied for layout or precision conversion. Do not
mutate or resize the input or any alias until the call returns.

See Also
--------
lapjvh : The other completion strategy with the same input/output contract.
lapjvr_batch : Solve a batch with reusable native workers.

Examples
--------
>>> import lap
>>> import numpy as np
>>> cost = np.array([[3.0, 1.0], [1.0, 4.0]])
>>> total, rows, cols = lap.lapjvr(cost)
>>> total, rows.tolist(), cols.tolist()
(2.0, [0, 1], [1, 0])
>>> lap.lapjvr(cost, return_cost=False, output='pairs').tolist()
[[0, 1], [1, 0]]
"""
lapjvh: _SingleSolver
"""Solve a cost matrix with Rust initialization and C++ completion.

Return aligned row and column indices or assignment pairs. When
return_cost=True, prepend the total cost of the selected matches.

Parameters
----------
cost : array_like, shape (N, M)
    Real numeric assignment costs. With precision='native', float32 and
    float64 inputs retain their cost precision. Other real numeric dtypes
    are normalized to float64.
    Positive infinity forbids an edge. Exclude NaN and negative infinity
    before calling; the solver does not check for these invalid values.
extend_cost : bool, default False
    Permit a rectangular matrix when cost_limit is infinite. Rectangular
    problems use a native path without padding to a square matrix. A finite
    cost_limit permits rectangular inputs regardless of this option.
cost_limit : float, default np.inf
    A finite limit permits unmatched rows and columns, each charged half
    the limit during optimization. The returned total excludes these
    penalties. Negative finite limits are allowed. With np.inf, require
    min(N, M) matches. NaN and negative infinity are invalid limits.
return_cost : bool, default True
    Prepend the total assignment cost if True. The total is accumulated in
    float64 from the selected input costs before any float32 downcast.
    False returns only indices or pairs and skips the total-cost sum.
precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
    Select the working cost precision. 'native' preserves float32/float64
    inputs and uses float64 for other real numeric inputs. Explicit
    'float32' or 'float64' converts the working costs. Finite costs and
    limits must fit the selected float32 range when float32 is used.
output : {'indices', 'pairs'}, keyword-only, default 'indices'
    'indices' returns aligned row and column arrays. 'pairs' returns a
    two-column array whose rows contain (row_index, column_index).

Returns
-------
total_cost : float, optional
    Present first only when return_cost=True. Sum of selected original
    costs, excluding unmatched penalties, even for finite cost_limit.
rows, cols : np.ndarray, shape (K,), dtype int64
    Returned when output='indices'. rows[i] is matched to cols[i]. Rows are
    sorted in increasing order; indices refer to the original matrix.
pairs : np.ndarray, shape (K, 2), dtype int64
    Returned instead of rows and cols when output='pairs'. K is at most
    min(N, M); finite limits can choose fewer matches. An empty dimension
    returns empty indices or pairs of shape (0, 2), with total 0.0.

Raises
------
TypeError
    cost has a non-real numeric dtype, such as complex, object, or string.
ValueError
    The input is not 2D, a nonempty rectangle is disallowed, an option or
    limit is invalid, float32 conversion overflows, dimensions exceed
    native limits, required matches are infeasible, or reduced costs
    overflow.
MemoryError
    An input copy, output array, or native workspace cannot be allocated.
RuntimeError
    C++ completion is unavailable, or an internal native error occurs.

Notes
-----
LAPJVH uses Rust initialization/reduction and C++ completion for
required square problems. Rectangular and finite-limit problems use
the same native Rust paths as LAPJVR, without square padding.

Required square problems use float64 search state even with float32 costs.
Rectangular and finite-limit paths use the selected working precision.
A finite limit optimizes rejection jointly with matching; it is not
equivalent to filtering a required solution after solving. Equal-cost
optima can produce different assignments across solvers or precisions.

Suitable contiguous arrays are borrowed and the native solve releases the
GIL. Other inputs may be copied for layout or precision conversion. Do not
mutate or resize the input or any alias until the call returns.

See Also
--------
lapjvr : The other completion strategy with the same input/output contract.
lapjvh_batch : Solve a batch with reusable native workers.

Examples
--------
>>> import lap
>>> import numpy as np
>>> cost = np.array([[3.0, 1.0], [1.0, 4.0]])
>>> total, rows, cols = lap.lapjvh(cost)
>>> total, rows.tolist(), cols.tolist()
(2.0, [0, 1], [1, 0])
>>> lap.lapjvh(cost, return_cost=False, output='pairs').tolist()
[[0, 1], [1, 0]]
"""
lapjvr_batch: _BatchSolver
"""Solve a batch with the Rust Jonker-Volgenant solver.

Solve each (N, M) matrix in a (B, N, M) batch and preserve input order.
Return lists of aligned indices or pair arrays, with optional totals.

Parameters
----------
costs : array_like, shape (B, N, M)
    Real numeric assignment costs. With precision='native', float32 and
    float64 inputs retain their cost precision. Other real numeric dtypes
    are normalized to float64.
    Positive infinity forbids an edge. Exclude NaN and negative infinity
    before calling; the solver does not check for these invalid values.
extend_cost : bool, default False
    Permit rectangular problems when cost_limit is infinite. Rectangles
    use native paths without square padding. A finite cost_limit permits
    rectangular problems regardless of this option.
cost_limit : float, default np.inf
    A finite limit permits unmatched rows and columns, each charged half
    the limit during optimization. Returned totals exclude these penalties.
    Negative finite limits are allowed. With np.inf, each problem requires
    min(N, M) matches. NaN and negative infinity are invalid limits.
return_cost : bool, default True
    Prepend the totals array if True. Totals are accumulated in float64
    from selected input costs before any float32 downcast. False returns
    only index lists or pair lists and skips the total-cost sums.
n_threads : int or None, default 0
    0 or None selects os.cpu_count(), using one if unavailable, capped by B.
    Automatic mode may run small workloads serially. One or negative
    values select serial execution. Positive values request reusable
    native workers, capped by B; there is no fixed worker-count ceiling.
    Empty and singleton batches do not require a worker pool.
precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
    Select the working cost precision. 'native' preserves float32/float64
    inputs and uses float64 for other real numeric inputs. Explicit
    'float32' or 'float64' converts the working costs. Finite costs and
    limits must fit the selected float32 range when float32 is used.
output : {'indices', 'pairs'}, keyword-only, default 'indices'
    'indices' returns two lists of aligned index arrays. 'pairs' returns
    one list of two-column assignment arrays.

Returns
-------
totals : np.ndarray, shape (B,), dtype float64, optional
    Present first only when return_cost=True. Each total sums selected
    original costs and excludes unmatched penalties.
rows_list, cols_list : list of np.ndarray
    Returned when output='indices'. Each list has length B. Entry b has
    shape (K_b,) and dtype int64, with rows sorted in increasing order.
    rows_list[b][i] is matched to cols_list[b][i] in the original matrix.
pairs_list : list of np.ndarray
    Returned instead of the two index lists when output='pairs'. Entry b
    has shape (K_b, 2) and dtype int64, containing (row_index, column_index).
    K_b is at most min(N, M); finite limits can choose fewer matches.
    B=0 returns empty lists and, when requested, empty totals. An empty
    matrix dimension returns empty assignments and zero totals for each b.

Raises
------
TypeError
    costs has a non-real numeric dtype, or n_threads cannot be interpreted
    as an integer.
ValueError
    The input is not 3D, nonempty rectangles are disallowed, options or
    thread counts are invalid, float32 conversion overflows, dimensions
    exceed native limits, required matches are infeasible, or reduced
    costs overflow. Native solver failures identify the lowest failing
    batch index; no partial batch result is returned.
MemoryError
    Input copies, outputs, native workspaces, or workers cannot be allocated.
RuntimeError
    An internal native solver error occurs.

Notes
-----
LAPJVR uses Rust for required square completion. Rectangular and
finite-limit problems use native Rust paths without square padding.

Required square problems use float64 search state even with float32 costs.
Rectangular and finite-limit paths use the selected working precision.
Finite limits optimize rejection jointly with matching; they are not
equivalent to filtering required solutions after solving. Equal-cost
optima can produce different assignments across solvers or precisions.

The native solve releases the GIL. Suitable contiguous arrays are borrowed;
other inputs may be copied for layout or precision conversion. Do not
mutate or resize the input or any alias until the call returns.

Both families share reusable native worker pools and workspaces. Calls may
run concurrently, and each call keeps its own completion strategy. Avoid
oversubscribing CPU cores with concurrent large batches. Use process
spawning instead of forking after native worker pools have initialized.

See Also
--------
lapjvr : Solve one matrix with the same precision and output options.
lapjvh_batch : The other completion strategy with the same batch contract.

Examples
--------
>>> import lap
>>> import numpy as np
>>> costs = np.array([[[3.0, 1.0], [1.0, 4.0]],
...                   [[4.0, 2.0], [3.0, 6.0]]])
>>> totals, rows, cols = lap.lapjvr_batch(costs, n_threads=2)
>>> totals.tolist()
[2.0, 5.0]
>>> [r.tolist() for r in rows]
[[0, 1], [0, 1]]
>>> pairs = lap.lapjvr_batch(costs, return_cost=False,
...                              output='pairs', n_threads=2)
>>> [p.tolist() for p in pairs]
[[[0, 1], [1, 0]], [[0, 1], [1, 0]]]
"""
lapjvh_batch: _BatchSolver
"""Solve a batch with Rust initialization and C++ completion.

Solve each (N, M) matrix in a (B, N, M) batch and preserve input order.
Return lists of aligned indices or pair arrays, with optional totals.

Parameters
----------
costs : array_like, shape (B, N, M)
    Real numeric assignment costs. With precision='native', float32 and
    float64 inputs retain their cost precision. Other real numeric dtypes
    are normalized to float64.
    Positive infinity forbids an edge. Exclude NaN and negative infinity
    before calling; the solver does not check for these invalid values.
extend_cost : bool, default False
    Permit rectangular problems when cost_limit is infinite. Rectangles
    use native paths without square padding. A finite cost_limit permits
    rectangular problems regardless of this option.
cost_limit : float, default np.inf
    A finite limit permits unmatched rows and columns, each charged half
    the limit during optimization. Returned totals exclude these penalties.
    Negative finite limits are allowed. With np.inf, each problem requires
    min(N, M) matches. NaN and negative infinity are invalid limits.
return_cost : bool, default True
    Prepend the totals array if True. Totals are accumulated in float64
    from selected input costs before any float32 downcast. False returns
    only index lists or pair lists and skips the total-cost sums.
n_threads : int or None, default 0
    0 or None selects os.cpu_count(), using one if unavailable, capped by B.
    Automatic mode may run small workloads serially. One or negative
    values select serial execution. Positive values request reusable
    native workers, capped by B; there is no fixed worker-count ceiling.
    Empty and singleton batches do not require a worker pool.
precision : {'native', 'float32', 'float64'}, keyword-only, default 'native'
    Select the working cost precision. 'native' preserves float32/float64
    inputs and uses float64 for other real numeric inputs. Explicit
    'float32' or 'float64' converts the working costs. Finite costs and
    limits must fit the selected float32 range when float32 is used.
output : {'indices', 'pairs'}, keyword-only, default 'indices'
    'indices' returns two lists of aligned index arrays. 'pairs' returns
    one list of two-column assignment arrays.

Returns
-------
totals : np.ndarray, shape (B,), dtype float64, optional
    Present first only when return_cost=True. Each total sums selected
    original costs and excludes unmatched penalties.
rows_list, cols_list : list of np.ndarray
    Returned when output='indices'. Each list has length B. Entry b has
    shape (K_b,) and dtype int64, with rows sorted in increasing order.
    rows_list[b][i] is matched to cols_list[b][i] in the original matrix.
pairs_list : list of np.ndarray
    Returned instead of the two index lists when output='pairs'. Entry b
    has shape (K_b, 2) and dtype int64, containing (row_index, column_index).
    K_b is at most min(N, M); finite limits can choose fewer matches.
    B=0 returns empty lists and, when requested, empty totals. An empty
    matrix dimension returns empty assignments and zero totals for each b.

Raises
------
TypeError
    costs has a non-real numeric dtype, or n_threads cannot be interpreted
    as an integer.
ValueError
    The input is not 3D, nonempty rectangles are disallowed, options or
    thread counts are invalid, float32 conversion overflows, dimensions
    exceed native limits, required matches are infeasible, or reduced
    costs overflow. Native solver failures identify the lowest failing
    batch index; no partial batch result is returned.
MemoryError
    Input copies, outputs, native workspaces, or workers cannot be allocated.
RuntimeError
    C++ completion is unavailable, or an internal native error occurs.

Notes
-----
LAPJVH uses Rust initialization/reduction and C++ completion for
required square problems. Rectangular and finite-limit problems use
the same native Rust paths as LAPJVR, without square padding.

Required square problems use float64 search state even with float32 costs.
Rectangular and finite-limit paths use the selected working precision.
Finite limits optimize rejection jointly with matching; they are not
equivalent to filtering required solutions after solving. Equal-cost
optima can produce different assignments across solvers or precisions.

The native solve releases the GIL. Suitable contiguous arrays are borrowed;
other inputs may be copied for layout or precision conversion. Do not
mutate or resize the input or any alias until the call returns.

Both families share reusable native worker pools and workspaces. Calls may
run concurrently, and each call keeps its own completion strategy. Avoid
oversubscribing CPU cores with concurrent large batches. Use process
spawning instead of forking after native worker pools have initialized.

See Also
--------
lapjvh : Solve one matrix with the same precision and output options.
lapjvr_batch : The other completion strategy with the same batch contract.

Examples
--------
>>> import lap
>>> import numpy as np
>>> costs = np.array([[[3.0, 1.0], [1.0, 4.0]],
...                   [[4.0, 2.0], [3.0, 6.0]]])
>>> totals, rows, cols = lap.lapjvh_batch(costs, n_threads=2)
>>> totals.tolist()
[2.0, 5.0]
>>> [r.tolist() for r in rows]
[[0, 1], [0, 1]]
>>> pairs = lap.lapjvh_batch(costs, return_cost=False,
...                              output='pairs', n_threads=2)
>>> [p.tolist() for p in pairs]
[[[0, 1], [1, 0]], [[0, 1], [1, 0]]]
"""
