from pqp.symbols import *
from pqp.data.domain import make_domain, CategoricalDomain, RealDomain, BinaryDomain, infer_domain_type
from pqp.causal.graph import DirectedEdge, BidirectedEdge

import pytest
import numpy as np
import pandas as pd

def test_infix():
    x, y, z = make_vars("xyz")
    assert (y <= x) == DirectedEdge(x, y)
    assert (x & y) == BidirectedEdge(x, y)
    assert (z <= [x, y]) == [DirectedEdge(x, z), DirectedEdge(y, z)]
    assert (x & [y, z]) == [BidirectedEdge(x, y), BidirectedEdge(x, z)]
    assert ((x <= y) <= z) == (DirectedEdge(y, x) <= z)

def test_event_infix():
    x, y = make_vars("xy")
    assert (x.val == 1) == EqualityEvent(x, 1)
    with pytest.raises(ValueError):
        x.val == y
    with pytest.raises(ValueError):
        x.val == y.val