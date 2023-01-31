from pqp.graph import Graph, make_vars
from pqp.utils import recursive_sort


# def test_create_graph():
#     x, y, z = make_vars("xyz")

#     g = Graph([
#         z <= x,
#         y <= z,
#         x & y
#     ])

#     assert recursive_sort(g.bi_edge_tuples()) == recursive_sort([("x", "y")])
#     assert recursive_sort(g.di_edge_tuples()) == recursive_sort([("x", "z"), ("y", "z")])

#     g.add_edge(x & z)

#     assert recursive_sort(g.bi_edge_tuples()) == recursive_sort([("x", "y"), ("x", "z")])

def test_id():
    x, y, z = make_vars("xyz")
    g = Graph([
        z <= x,
        y <= z,
        x & y
    ])
    estimand = g.idc([y], [x])

    print(estimand.to_latex())
    
    assert estimand != None
    assert False