from pqp.utils import *
from pytest import raises

def test_order_graph():
    g = {
        1: [2, 3],
        2: [4],
        3: [4],
    }
    assert order_graph(g) == [1, 2, 3, 4]

    g = {
        1: [7, 8],
        2: [3],
        3: [4],
        4: [5],
        5: [6],
        6: [7],
        7: [8],
    }
    assert order_graph(g) == [1, 2, 3, 4, 5, 6, 7, 8]

    g = {}
    assert order_graph(g) == []

    with raises(Exception):
        g = {
            1: [2],
            2: [3],
            3: [1],
        }
        order_graph(g)
