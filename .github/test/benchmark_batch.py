import os
import lap
import time
import numpy as np


def do_lapx_loop(cost_matrix_batch,  extend_cost=False, backend='lapjvx'):
    total_cost = 0.0
    assignments = []
    for cost_matrix in cost_matrix_batch:
        if backend == 'lapjvs':
            cost, row_indices, col_indices = lap.lapjvs(cost_matrix, extend_cost=extend_cost, return_cost=True)
            assignments.append(np.stack([row_indices, col_indices], axis=1))
        elif backend == 'lapjvx':
            cost, row_indices, col_indices = lap.lapjvx(cost_matrix, extend_cost=extend_cost, return_cost=True)
            assignments.append(np.stack([row_indices, col_indices], axis=1))
        total_cost += cost
    return total_cost, assignments


if __name__ == "__main__":

    for b, n, m in [(50, 3000, 3000), (100, 2000, 2000), (500, 1000, 2000), (1000, 1000, 1000)]:

        batch_size = b
        batch_costs = np.random.rand(batch_size, n, m)

        # number of threads
        n_threads = os.cpu_count()
        # n_threads = 8  # override for testing

        # extend_cost 
        extend_cost = True if n != m else False

        # benchmarking INFO
        print(f"\n# {batch_size} x ({n}x{m}) | n_threads = {n_threads} \n")

        # warm-up
        warmup_costs = np.random.rand(10, 500, 500)

        # batch - LAPX - lapjvx_batch
        lap.lapjvx_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)  # warm-up
        t0 = time.time()
        _c_lapjvx_batch, rows, cols = lap.lapjvx_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)
        c_lapjvx_batch = _c_lapjvx_batch.sum()
        t_lapjvx_batch = time.time() - t0
        print(f"  CPU lapx-batch-jvx     :  cost={c_lapjvx_batch:.8f}, time={t_lapjvx_batch:.8f}s")

        # batch - LAPX - lapjvs_batch
        lap.lapjvs_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)  # warm-up
        t0 = time.time()
        _c_lapjvs_batch, rows, cols = lap.lapjvs_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)
        c_lapjvs_batch = _c_lapjvs_batch.sum()
        t_lapjvs_batch = time.time() - t0
        print(f"  CPU lapx-batch-jvs     :  cost={c_lapjvs_batch:.8f}, time={t_lapjvs_batch:.8f}s")

        # batch - LAPX - lapjvxa_batch
        lap.lapjvxa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)  # warm-up
        t0 = time.time()
        _c_lapx_batch, a_lapx_batch = lap.lapjvxa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)
        c_lapx_batch = _c_lapx_batch.sum()
        t_lapx_batch = time.time() - t0
        print(f"  CPU lapx-batch-jvxa    :  cost={c_lapx_batch:.8f}, time={t_lapx_batch:.8f}s")

        # batch - LAPX - lapjvsa_batch
        lap.lapjvsa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)  # warm-up
        t0 = time.time()
        _c_lapx_batch2, a_lapx_batch2 = lap.lapjvsa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads)
        c_lapx_batch2 = _c_lapx_batch2.sum()
        t_lapx_batch2 = time.time() - t0
        print(f"  CPU lapx-batch-jvsa    :  cost={c_lapx_batch2:.8f}, time={t_lapx_batch2:.8f}s")

        # batch - LAPX - lapjvsa_batch float64
        lap.lapjvsa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads, prefer_float32=False)  # warm-up
        t0 = time.time()
        _c_lapx_batch3, a_lapx_batch3 = lap.lapjvsa_batch(batch_costs, return_cost=True, extend_cost=extend_cost, n_threads=n_threads, prefer_float32=False)
        c_lapx_batch3 = _c_lapx_batch3.sum()
        t_lapx_batch3 = time.time() - t0
        print(f"  CPU lapx-batch-jvsa64  :  cost={c_lapx_batch3:.8f}, time={t_lapx_batch3:.8f}s")

        # LAPX - lapjvx - Loop over batch
        do_lapx_loop(warmup_costs, extend_cost=extend_cost, backend='lapjvx')  # warm-up
        t0 = time.time()
        c_lapx, a_lapx = do_lapx_loop(batch_costs, extend_cost=extend_cost, backend='lapjvx')
        t_lapx = time.time() - t0
        print(f"  CPU lapx-loop-jvx      :  cost={c_lapx:.8f}, time={t_lapx:.8f}s")

        # LAPX - lapjvs - Loop over batch
        do_lapx_loop(warmup_costs, extend_cost=extend_cost, backend='lapjvs')  # warm-up
        t0 = time.time()
        c_lapx1, a_lapx1 = do_lapx_loop(batch_costs, extend_cost=extend_cost, backend='lapjvs')
        t_lapx1 = time.time() - t0
        print(f"  CPU lapx-loop-jvs      :  cost={c_lapx1:.8f}, time={t_lapx1:.8f}s")
