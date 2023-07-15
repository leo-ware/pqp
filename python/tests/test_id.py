from pqp.utils import recursive_sort
from pqp.symbols import *
from pqp.symbols.parse import parse_json
from pqp.identification.graph import Graph

def test_fd():
    x, y, z = make_vars("xyz")
    g = Graph([
        z <= x,
        y <= z,
        x & y
    ])
    estimand = g._idc([y], [x])
    ans = Marginal(z, (Marginal(x, P([x])*P([x, y, z])/P([x, z])) * P([x, z]))/P([x]))
    assert estimand == ans

def test_bd():
    x, y, z = make_vars("xyz")
    g = Graph([
        x <= z,
        y <= z,
        y <= x
    ])
    estimand = g._idc([y], [x])
    ans = Marginal(z, (P([z])*P([x, y, z]))/P([x, z]))
    assert estimand == ans

# def test_irrelevant():
#     x, y, z = make_vars("xyz")
#     g1 = Graph([y <= x, z <= x])
#     g2 = Graph([y <= x, y <= z])
#     assert g1.idc([y], [x]) == g2.idc([y], [x])

# def test_irrelevant_mediator():
#     x, y, z, m  = make_vars("xyzm")
#     g1 = Graph([
#         x <= z,
#         m <= x,
#         y <= [m, z],
#     ])
#     g2 = Graph([
#         x <= z,
#         m <= x,
#         y <= [x, z],
#     ])
#     assert g1.idc([y], [x]) == g2.idc([y], [x])

# def test_ate():
#     x, y, z = make_vars("xyz")
#     g = Graph([
#         x <= z,
#         y <= z,
#         y <= x
#     ])
#     estimand = g.ate(y, x)
#     assert estimand is not None

# def test_repr_expression():
#     x, y, z = make_vars("xyz")
#     assert str(x / y) == "[x / y]"
#     assert str(x * y) == "x * y"
#     assert (x / y).to_latex() == "{x \\over y}"
#     assert (x * y).to_latex() == "x y"
