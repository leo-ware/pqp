# from pqp import Graph, make_vars
# from pqp.utils import recursive_sort


# def test_create_graph():
#     x, y, z = make_vars("xyz")

#     g = Graph([
#         z <= x,
#         y <= z,
#         x & y
#     ])
#     assert recursive_sort(g._bi_edge_tuples()) == recursive_sort([("x", "y")])
#     assert recursive_sort(g._di_edge_tuples()) == recursive_sort([("x", "z"), ("y", "z")])

#     g.add_edge(x & z)
#     assert recursive_sort(g._bi_edge_tuples()) == recursive_sort([("x", "y"), ("x", "z")])

# def test_id():
#     x, y, z = make_vars("xyz")
#     g = Graph([
#         z <= x,
#         y <= z,
#         x & y
#     ])
#     estimand = g._idc([y], [x])    
#     assert estimand != None

# def test_repr_expression():
#     x, y, z = make_vars("xyz")
#     assert str(x / y) == "[x / y]"
#     assert str(x * y) == "x * y"
#     assert (x / y).to_latex() == "{x \over y}"
#     assert (x * y).to_latex() == "x y"