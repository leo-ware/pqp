from pqp.symbols import *
from pqp.causal.graph import Graph
from pqp.utils import recursive_sort


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

def test_identify():
    x, y, z, m = make_vars("xyzm")
    g = Graph([
        x <= z,
        y <= [z, x],
        m <= y,
    ])
    assert g.identify(P(y, given=do(x))) == g.idc([y], [x])
    assert g.identify(P(y, given=do(m))) == P(y)
    assert g.identify(P(x, given=[do(m), do(y)])) == P(x)
    assert g.identify(P(x) - P(y, given=do(x))) == P(x) - g.identify(P(y, given=[do(x)]))
    assert g.identify(Expectation(x, P(x, given=[do(y)]))) == Expectation(x, P(x))
