from solver import *


b = Board()
b.load("test")
b("N3", "fut")
print(b)

sol = b.rows[13].solve("etables")
print(sol)
# sol = b.solve("etables")
for i in sol[:10]:
    print(i)