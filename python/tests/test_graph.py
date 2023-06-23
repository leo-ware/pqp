from pqp.symbols import *
from pqp.identification.graph import Graph, SearchNode
from pqp.utils import recursive_sort

from pytest import raises


def test_create_graph():
    x, y, z = make_vars("xyz")

    g = Graph([
        z <= x,
        y <= z,
        x & y
    ])
    assert recursive_sort(g._bi_edge_tuples()) == recursive_sort([("x", "y")])
    assert recursive_sort(g._di_edge_tuples()) == recursive_sort([("x", "z"), ("y", "z")])

    g.add_edge(x & z)
    assert recursive_sort(g._bi_edge_tuples()) == recursive_sort([("x", "y"), ("x", "z")])

def test_identify():
    x, y, z, m = make_vars("xyzm")
    g = Graph([
        x <= z,
        y <= [z, x],
        m <= y,
    ])
    assert g.identify(P(y, given=do(x))).identified_estimand == g._idc([y], [x])
    assert g.identify(P(y, given=do(m))).identified_estimand == P(y)
    assert g.identify(P(x, given=[do(m), do(y)])).identified_estimand == P(x)
    assert g.identify(P(x) - P(y, given=do(x))).identified_estimand == P(x) - g.identify(P(y, given=[do(x)])).identified_estimand
    assert g.identify(Expectation(x, P(x, given=[do(y)]))).identified_estimand == Expectation(x, P(x))

def test_search_node():
    a = SearchNode(None, "a")
    b = SearchNode(a, "b")
    c = SearchNode(b, "c")

    assert a.unpack() == ["a"]
    assert b.unpack() == ["a", "b"]
    assert c.unpack() == ["a", "b", "c"]
    
    with raises(TypeError):
        SearchNode(None)
    with raises(TypeError):
        SearchNode()

def test_dir_edge_dict():
    a, b, c = make_vars("abc")
    g = Graph([
        a <= b,
        b <= c,
        c <= a,
    ])
    edges = g.dir_edge_dict()
    assert set(edges[a]) == {c}
    assert set(edges[b]) == {a}
    assert set(edges[c]) == {b}


def test_dfs():
    a, b, c, d, e = make_vars("abcde")
    g = Graph([
        b <= a,
        c <= b,
        d <= c,
        d <= a
    ])

    paths_ad = {tuple(path) for path in g.dfs(a, d)}
    assert paths_ad == {(a, b, c, d), (a, d)}

    paths_bd = {tuple(path) for path in g.dfs(b, d)}
    assert paths_bd == {(b, c, d)}

    paths_ca = {tuple(path) for path in g.dfs(c, a)}
    assert paths_ca == set()

    paths_aa = {tuple(path) for path in g.dfs(a, a)}
    assert paths_aa == {(a,)}

    with raises(ValueError):
        g.dfs(a, e)
