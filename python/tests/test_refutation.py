import numpy as np
import pandas as pd
from pqp.data.data import Data
from pqp.identification.graph import Graph
from pqp.estimation import MultinomialEstimator
from pqp.identification.estimands import *
from pqp.symbols import *

def test_explain():
    x, y, z = make_vars("xyz")
    df = pd.DataFrame({
        "x": [0, 1, 0, 1, 1.5, 1.5],
        "y": [0, 1, 1, 2, 1.5, 2.5],
        "m": [1, 2, 3, 4, 5, 6],
        "z": [0, 0, 1, 1, 0, 1],
    })
    data = Data(df)

    dist = MultinomialEstimator(data, prior=0.1)
    dist.explain(nested=True)

    causal_estimand = ATE(y, {z: 0}, {z: 1})

    x, y, z, m = make_vars("xyzm")

    g = Graph([
        y <= [x, z],
        x <= z,
        m <= x,
    ])

    estimand = g.identify(causal_estimand)
    estimand.explain()

    est = dist.estimate(estimand)
    est.explain()
