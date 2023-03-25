import pandas as pd
from pqp.estimation.model import Model
from pqp.causal.graph import Graph
from pqp.parametric.categorical_distribution import CategoricalDistribution
from pqp.data.data import Data
from pqp.symbols import *

def test_approx_p_no_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]})
    data = Data(df, {"x": "binary", "y": "binary"})
    dist = CategoricalDistribution(data, prior=0)

    y1_given_x1 = dist.approx(P([data.vars.y.val == 1], given=[data.vars.x.val == 1]))
    assert y1_given_x1 == 0.5

    y1_given_x0 = dist.approx(P([data.vars.y.val == 1], given=[data.vars.x.val == 0]))
    assert y1_given_x0 == 0.0

def test_approx_p_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]})
    data = Data(df)
    dist = CategoricalDistribution(data, prior=1)

    y1_given_x1 = dist.approx(
        P([data.vars.y], given=[data.vars.x]),
        {"x": 1, "y": 1}
        )
    assert y1_given_x1 == 0.5

    y1_given_x0 = dist.approx(
        P([data.vars.y], given=[data.vars.x]),
        {"x": 0, "y": 1}
        )
    assert y1_given_x0 == 1/6

    y1 = dist.approx(
        P([data.vars.y]),
        {"y": 1}
        )
    assert y1 == 3/8

def test_assignments_args():
    data = Data(pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]}))
    dist = CategoricalDistribution(data)

    x = data.vars.x
    y = data.vars.y

    exp = P(x)
    assert dist.approx(exp, {"x": 1, "y": 1}) == \
        dist.approx(exp.assign(x, 1).assign(y, 1))

    exp = Expectation(x, P(x, given=y)) * P(y)
    dist.approx(exp, {"x": 1, "y": 1})
    assert dist.approx(exp, {"x": 1, "y": 1}) ==\
        dist.approx(exp.assign(x, 1).assign(y, 1))

    exp = P(y, given=x) * P([x, y]) / P(y) * Marginal(y, P(y, given=x))
    assert dist.approx(exp, {"x": 1, "y": 1}) ==\
        dist.approx(exp.assign(x, 1).assign(y, 1))

    exp = P([x, y]) - P(y)
    assert dist.approx(exp, {"x": 1, "y": 1}) == \
        dist.approx(exp.assign(x, 1).assign(y, 1))
    

def test_approx_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 1], "z": [0, 0, 1]})
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    dist = CategoricalDistribution(data, prior=1)

    context = {"x": 1, "z": 0}
    assert (
        dist.approx(Quotient(P([data.vars.x, data.vars.z]), P([data.vars.z])), context) == 
        dist.approx(P([data.vars.x], given=[data.vars.z]), context)
        )


def test_approx_prior_more():
    df = pd.DataFrame({"x": [0], "y": [0], "z": [0]})
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    assert data.vars['x'].domain.get_cardinality() == 2

    dist = CategoricalDistribution(data, prior=1)

    joint = P([data.vars.x, data.vars.y, data.vars.z])
    zeros = {"x": 0, "y": 0, "z": 0}
    ones = {"x": 1, "y": 1, "z": 1}

    p_zeros = dist.approx(joint, zeros)
    p_ones = dist.approx(joint, ones)
    assert p_zeros == (1/2 * 1/8) + (1/2 * 1)   # 50/50 prior/data because only one sample
                                                # p=1/8 under prior, p=1 under data
    assert p_ones == (1/2 * 1/8) + (1/2 * 0)    # p=1/8 under prior, p=0 under data

    cond_z = P([data.vars.x, data.vars.y], given=[data.vars.z])
    p_zeros_cond_z = dist.approx(cond_z, zeros)
    p_ones_cond_z = dist.approx(cond_z, ones)
    assert p_zeros_cond_z == (1 + 1/8)/(1 + 4/8)    # data chance (1) plus prior chance (1/8), normalized
    assert p_ones_cond_z == 1/4     # four options once z = 1, none in dataset


def test_approx_nested():
    df = pd.DataFrame({"x": [0, 0, 1, 1], "y": [0, 1, 0, 1]})
    data = Data(df, {"x": "binary", "y": "binary"})
    dist = CategoricalDistribution(data, prior=0)

    y1 = dist.approx(
        Marginal([data.vars.x], P([data.vars.y, data.vars.x])),
        {"y": 1}
        )
    assert y1 == 1/2

    y0 = dist.approx(
        Product([P([data.vars.y]), Quotient(P([data.vars.y, data.vars.x]), P([data.vars.x]))]),
        {"y": 0, "x": 0}
        )
    assert y0 == 0.5*(0.25 / 0.5)