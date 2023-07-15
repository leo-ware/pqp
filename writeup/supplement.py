from pqp.symbols import make_vars
from pqp.identification import Graph
import matplotlib.pyplot as plt


x, y, z, z1, z2, z3 = make_vars(["x", "y", "z", "z1", "z2", "z3"])

g1 = Graph([y <= x])
g2 = Graph([
    y <= x,
    z <= x,
    y <= z,
    z & y
])
g3 = Graph([
    x <= z,
    y <= z,
    y <= x,
    z & y
])
g4 = Graph([
    x <= z,
    y <= x,
    y <= z,
    x & z
])
g5 = Graph([
    z <= x,
    y <= z,
    x & y
])
g6 = Graph([
    y <= x,
    y <= z1,
    y <= z2,
    z1 <= x,
    z2 <= z1,
    x & z2,
    y & z1,
])
g7 = Graph([
    x <= z2,
    z1 <= x,
    z1 <= z2,
    z3 <= z2,
    y <= z1,
    y <= z3,
    x & y,
    x & z3,
    x & z2,
    y & z2,
])
