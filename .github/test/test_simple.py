import lap
import numpy as np


if __name__ == "__main__":

    print("\n=================== Testing Single-matrix Solvers ===================\n")

    cost_matrix = np.random.rand(4, 5)
    print(f"\nCost matrix (4x5):\n\n{cost_matrix}\n")

    print("\n---------- lap.lapjv() ----------\n")
    print(lap.lapjv(cost_matrix, extend_cost=True, return_cost=True))

    print("\n---------- lap.lapjvx() ----------\n")
    print(lap.lapjvx(cost_matrix, extend_cost=True, return_cost=True))

    print("\n---------- lap.lapjvxa() ----------\n")
    print(lap.lapjvxa(cost_matrix, extend_cost=True, return_cost=True))

    print("\n---------- lap.lapjvc() ----------\n")
    print(lap.lapjvc(cost_matrix, return_cost=True))

    print("\n---------- lap.lapjvs() ----------\n")
    print(lap.lapjvs(cost_matrix, extend_cost=True, return_cost=True))

    print("\n---------- lap.lapjvsa() ----------\n")
    print(lap.lapjvsa(cost_matrix, extend_cost=True, return_cost=True))

    print("\n=================== Testing Batch-matrix Solvers ===================\n")

    batch_costs = np.random.rand(3, 4, 5)
    print(f"\nBatch cost (BxNxM) - (3x4x5):\n\n{batch_costs}\n")

    print("\n---------- lap.lapjvx_batch() ----------\n")
    print(lap.lapjvx_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=2))

    print("\n---------- lap.lapjvxa_batch() ----------\n")
    print(lap.lapjvxa_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=2))

    print("\n---------- lap.lapjvs_batch() ----------\n")
    print(lap.lapjvs_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=2))

    print("\n---------- lap.lapjvsa_batch() ----------\n")
    print(lap.lapjvsa_batch(batch_costs, extend_cost=True,  return_cost=True, n_threads=2))

