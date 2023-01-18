from sherlock_py import graph, expression

def test_create_graph():
    g = graph.Graph()
    assert g is not None