import lap
import numpy as np

cost_matrix = np.random.rand(4, 5)
print(f"\nCost matrix:\n\n{cost_matrix}\n")

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
