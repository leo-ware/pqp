import pandas as pd
from pqp.identification.graph import Graph
from pqp.estimation import MultinomialEstimator
from pqp.estimation.multinomial_estimator import _extract_assignments_expr
from pqp.data.data import Data
from pqp.symbols import *
from pqp.utils.exceptions import PositivityException
from pytest import raises

def test_approx_p_no_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]})
    data = Data(df, {"x": "binary", "y": "binary"})
    dist = MultinomialEstimator(data, prior=0)

    y1_given_x1 = dist.estimate(P([data.vars.y.val == 1], given=[data.vars.x.val == 1]))
    assert y1_given_x1.value == 0.5

    y1_given_x0 = dist.estimate(P([data.vars.y.val == 1], given=[data.vars.x.val == 0]))
    assert y1_given_x0.value == 0.0

def test_approx_p_no_prior_again():
    df = pd.DataFrame({
        "x": [0, 1, 0, 1],
        "z": [1, 1, 0, 1],
        "y": [1, 1, 0, 1],
    })
    dist = MultinomialEstimator(Data(df, {"x": "binary", "y": "binary", "z": "binary"}), prior=0)
    x, y, z = make_vars("xyz")

    assert dist.estimate(P(y.val == 1, given=z.val == 1)).value == 1
    assert dist.estimate(P(y.val == 1, given=z.val == 0)).value == 0
    assert dist.estimate(P(y.val == 0, given=x.val == 1)).value == 0
    assert dist.estimate(P(y.val == 0, given=x.val == 0)).value == 0.5

    assert dist.estimate(P(y.val == 1, given=x.val == 1)).value == 1
    assert dist.estimate(P(y.val == 1, given=x.val == 0)).value == 0.5
    assert dist.estimate(P(y.val == 0, given=x.val == 1)).value == 0
    assert dist.estimate(P(y.val == 0, given=x.val == 0)).value == 0.5

def test_approx_p_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]})
    data = Data(df)
    dist = MultinomialEstimator(data, prior=1)

    y1_given_x1 = dist.estimate(
        P([data.vars.y], given=[data.vars.x]),
        {"x": 1, "y": 1}
        )
    assert y1_given_x1.value == 0.5

    y1_given_x0 = dist.estimate(
        P([data.vars.y], given=[data.vars.x]),
        {"x": 0, "y": 1}
        )
    assert y1_given_x0.value == 1/6

    y1 = dist.estimate(
        P([data.vars.y]),
        {"y": 1}
        )
    assert y1.value == 3/8

def test_assignments_args():
    data = Data(pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 0]}))
    dist = MultinomialEstimator(data)

    x = data.vars.x
    y = data.vars.y

    exp = P(x)
    assert dist.estimate(exp, {"x": 1, "y": 1}).value == \
        dist.estimate(exp.assign(x, 1).assign(y, 1)).value

    exp = Expectation(x, P(x, given=y)) * P(y)
    assert dist.estimate(exp, {"x": 1, "y": 1}).value ==\
        dist.estimate(exp.assign(x, 1).assign(y, 1)).value

    exp = P(y, given=x) * P([x, y]) / P(y) * Marginal(y, P(y, given=x))
    assert dist.estimate(exp, {"x": 1, "y": 1}).value ==\
        dist.estimate(exp.assign(x, 1).assign(y, 1)).value

    exp = P([x, y]) - P(y)
    assert dist.estimate(exp, {"x": 1, "y": 1}).value == \
        dist.estimate(exp.assign(x, 1).assign(y, 1)).value
    

def test_approx_prior():
    df = pd.DataFrame({"x": [0, 1, 1], "y": [0, 1, 1], "z": [0, 0, 1]})
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    dist = MultinomialEstimator(data, prior=1)

    context = {"x": 1, "z": 0}
    assert (
        dist.estimate(Quotient(P([data.vars.x, data.vars.z]), P([data.vars.z])), context).value == 
        dist.estimate(P([data.vars.x], given=[data.vars.z]), context).value
        )


def test_approx_prior_more():
    df = pd.DataFrame({"x": [0], "y": [0], "z": [0]})
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    assert data.vars['x'].domain.get_cardinality() == 2

    dist = MultinomialEstimator(data, prior=1)

    joint = P([data.vars.x, data.vars.y, data.vars.z])
    zeros = {"x": 0, "y": 0, "z": 0}
    ones = {"x": 1, "y": 1, "z": 1}

    p_zeros = dist.estimate(joint, zeros)
    p_ones = dist.estimate(joint, ones)
    assert p_zeros.value == (1/2 * 1/8) + (1/2 * 1)   # 50/50 prior/data because only one sample
                                                      # p=1/8 under prior, p=1 under data
    assert p_ones.value == (1/2 * 1/8) + (1/2 * 0)    # p=1/8 under prior, p=0 under data

    cond_z = P([data.vars.x, data.vars.y], given=[data.vars.z])
    p_zeros_cond_z = dist.estimate(cond_z, zeros)
    p_ones_cond_z = dist.estimate(cond_z, ones)
    assert p_zeros_cond_z.value == (1 + 1/8)/(1 + 4/8)    # data chance (1) plus prior chance (1/8), normalized
    assert p_ones_cond_z.value == 1/4     # four options once z = 1, none in dataset


def test_approx_nested():
    df = pd.DataFrame({"x": [0, 0, 1, 1], "y": [0, 1, 0, 1]})
    data = Data(df, {"x": "binary", "y": "binary"})
    dist = MultinomialEstimator(data, prior=0)

    y1 = dist.estimate(
        Marginal([data.vars.x], P([data.vars.y, data.vars.x])),
        {"y": 1}
        )
    assert y1.value == 1/2

    y0 = dist.estimate(
        Product([P([data.vars.y]), Quotient(P([data.vars.y, data.vars.x]), P([data.vars.x]))]),
        {"y": 0, "x": 0}
        )
    assert y0.value == 0.5*(0.25 / 0.5)

def test_positivity_exception():
    df = pd.DataFrame({"x": [0, 1], "y": [1, 1]})
    data = Data(df, {"x": "binary", "y": "binary"})
    x, y = make_vars("xy")
    dist = MultinomialEstimator(data)
    with raises(PositivityException):
        print(dist.estimate(Expectation(x, P(x, given=y.val == 0))))

def test_where_conditions():
    df = pd.DataFrame({
        "x": [0, 1, 0, 1],
        "z": [1, 1, 0, 1],
        "y": [1, 1, 0, 1],
    })
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    dist = MultinomialEstimator(data, prior=0)
    x, y, z = make_vars("xyz")

    subset = dist._df_where_conditions({x: 1})
    assert subset.shape[0] == 2
    assert set(subset.columns.tolist()) == {"y", "z"}
    assert subset.y.tolist() == [1, 1]
    assert subset.z.tolist() == [1, 1]

    subset = dist._df_where_conditions({x: 1, y: 1})
    assert subset.shape[0] == 2
    assert set(subset.columns.tolist()) == {"z"}
    assert subset.z.tolist() == [1, 1]

    subset = dist._df_where_conditions({x: 0, z: 1})
    assert subset.shape[0] == 1
    assert set(subset.columns.tolist()) == {"y"}
    assert subset.y.tolist() == [1]

def test_count_where_conditions():
    df = pd.DataFrame({
        "x": [0, 1, 0, 1],
        "z": [1, 1, 0, 1],
        "y": [1, 1, 0, 1],
    })
    data = Data(df, {"x": "binary", "y": "binary", "z": "binary"})
    dist = MultinomialEstimator(data, prior=0)
    x, y, z = make_vars("xyz")

    assert dist._count_where_conditions({x: 1}, df) == 2
    assert dist._count_where_conditions({y: 1}, df) == 3
    assert dist._count_where_conditions({z: 1}, df) == 3
    assert dist._count_where_conditions({x: 1, y: 1}, df) == 2
    assert dist._count_where_conditions({x: 1, z: 1}, df) == 2
    assert dist._count_where_conditions({y: 1, z: 1}, df) == 3
    assert dist._count_where_conditions({y: 0, z: 1}, df) == 0
    assert dist._count_where_conditions({z: 0, y: 1}, df) == 0
    assert dist._count_where_conditions({x: 1, y: 1, z: 1}, df) == 2
    assert dist._count_where_conditions({x: 0, y: 1, z: 1}, df) == 1
    assert dist._count_where_conditions({x: 0, y: 0, z: 1}, df) == 0

def test_extract():
    x, y, z = make_vars("xyz")

    expr, context = _extract_assignments_expr(P(y.val == 1, given=z.val == 1))
    assert expr == P(y, given=z)
    assert context == {"y": 1, "z": 1}

    with raises(ValueError):
        print(_extract_assignments_expr(P(y.val == 1, given=do(x.val == 1))))
    
    with raises(ValueError):
        print(_extract_assignments_expr(P(y.val == 1, given=[z.val == 1, do(x.val == 1)])))
    
    with raises(ValueError):
        print(_extract_assignments_expr(P(y.val == 1, given=x)))
