from pqp.graph import Graph
from pqp.variable import make_vars
from pqp.utils import recursive_sort
from pqp.expression import Marginal, P


def test_create_graph():
    x, y, z = make_vars("xyz")

    g = Graph([
        z <= x,
        y <= z,
        x & y
    ])
    assert recursive_sort(g.bi_edge_tuples()) == recursive_sort([("x", "y")])
    assert recursive_sort(g.di_edge_tuples()) == recursive_sort([("x", "z"), ("y", "z")])

    g.add_edge(x & z)
    assert recursive_sort(g.bi_edge_tuples()) == recursive_sort([("x", "y"), ("x", "z")])

def test_fd():
    x, y, z = make_vars("xyz")
    g = Graph([
        z <= x,
        y <= z,
        x & y
    ])
    estimand = g.idc([y], [x])
    ans = Marginal(z, (Marginal(x, P([x])*P([x, y, z])/P([x, z])) * P([x, z]))/P([x]))

    print(estimand)
    print(ans)

    assert estimand == ans

def test_bd():
    x, y, z = make_vars("xyz")
    g = Graph([
        x <= z,
        y <= z,
        y <= x
    ])
    estimand = g.idc([y], [x])
    ans = Marginal(z, (P([z])*P([x, y, z]))/P([x, z]))

    print(estimand)
    print(ans)

    assert estimand == ans

def test_repr_expression():
    x, y, z = make_vars("xyz")
    assert str(x / y) == "[x / y]"
    assert str(x * y) == "x * y"
    assert (x / y).to_latex() == "{x \\over y}"
    assert (x * y).to_latex() == "x y"
