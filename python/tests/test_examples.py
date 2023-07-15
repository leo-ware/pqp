import numpy as np
import pandas as pd

from pqp.identification.graph import Graph
from pqp.identification.estimands import ATE, CATE
from pqp.data.data import Data
from pqp.estimation import Estimator, MultinomialEstimator
from pqp.symbols import *

def test_direct_effect_estimation():
    x, y = make_vars("xy")
    data = Data(pd.DataFrame({
        "x": [0, 0, 1, 1],
        "y": [0, 1, 0, 1],
    }))

    parametric_model = MultinomialEstimator(data)
    causal_model = Graph([y <= x])
    causal_estimand = ATE(y, treatment_condition={x: 1}, control_condition={x: 0})

    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    assert identified_estimand == (
        Expectation(y, P([x, y])/P(x)).assign(x, 1) -
        Expectation(y, P([x, y])/P(x)).assign(x, 0)
        )
    effect = parametric_model.estimate(identified_estimand)
    assert effect.value == 0


def test_direct_effect_estimation_again():
    x, y = make_vars("xy")
    data = Data(pd.DataFrame({
        "x": [0, 1, 1, 1],
        "y": [0, 1, 0, 1],
    }))

    parametric_model = MultinomialEstimator(data)
    causal_model = Graph([y <= x])
    causal_estimand = ATE(y, treatment_condition={x: 1}, control_condition={x: 0})

    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    assert identified_estimand == (
        Expectation(y, P([x, y])/P(x)).assign(x, 1) -
        Expectation(y, P([x, y])/P(x)).assign(x, 0)
        )
    effect = parametric_model.estimate(identified_estimand)
    assert effect.value == 2/3

def test_bd_estimation():
    x, y, z = make_vars("xyz")
    data = Data(pd.DataFrame({
        "x": [0, 1, 0, 1],
        "y": [0, 1, 1, 2],
        "z": [0, 0, 1, 1],
    }))

    parametric_model = MultinomialEstimator(data, prior=0.1)
    causal_model = Graph([
        y <= [x, z],
        x <= z,
        ])
    
    causal_estimand = ATE(y, treatment_condition={x: 1}, control_condition={x: 0})
    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    effect = parametric_model.estimate(identified_estimand)
    assert abs(effect.value - 1) < 0.05

    causal_estimand = ATE(y, treatment_condition={z: 1}, control_condition={z: 0})
    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    effect = parametric_model.estimate(identified_estimand)
    assert abs(effect.value - 1) < 0.05

    causal_estimand = ATE(z, treatment_condition={y: 1}, control_condition={y: 0})
    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    effect = parametric_model.estimate(identified_estimand)
    assert abs(effect.value) < 0.05

    causal_estimand = ATE(x, treatment_condition={z: 1}, control_condition={z: 0})
    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    effect = parametric_model.estimate(identified_estimand)
    assert abs(effect.value) < 0.05

    causal_estimand = CATE(y, treatment_condition={z: 1}, control_condition={z: 0}, subpopulation={x: 1})
    identified_estimand = causal_model.identify(causal_estimand).identified_estimand
    effect = parametric_model.estimate(identified_estimand)
    assert abs(effect.value - 1) < 0.05

def test_writeup_demo():
    x, y, z, m = make_vars("xyzm")

    df = pd.DataFrame()
    df["z"] = np.random.choice([0, 1], size=1000)
    df["x"] = (0.5*df.z + np.random.random(size=1000) > 0.75).astype(int)
    df["m"] = (0.5*df.x + np.random.random(size=1000) > 0.75).astype(int)
    df["y"] = df.m + df.z

    god_graph = Graph([
        x <= z,
        m <= x,
        y <= [z, m]
    ])
    model = MultinomialEstimator(df)
    ate = ATE(y, x)
    estimand = god_graph.identify(ate)
    model.estimate(estimand)


# def test_fd_estimation():
#     severity = np.array([0, 1])
#     treatment = severity                            # perfect doctor
#     pathway = (1-treatment)*0.3                     # treatment => 0, control => 0.5
#     outcome = (severity + pathway)                  # higher is worse

#     df = pd.DataFrame({
#         "severity": severity,
#         "treatment": treatment,
#         "pathway": pathway,
#         "outcome": outcome,
#     })

#     data = Data(df, {
#         "severity": "discrete",
#         "treatment": "discrete",
#         "pathway": "discrete",
#         "outcome": "discrete",
#     })

#     v = data.vars

#     naive_model = Model(
#         MultinomialEstimator(data, prior=0, observed=["outcome", "treatment"]),
#         Graph([v.outcome <= v.treatment])
#         )
#     naive_ate = naive_model.ate(
#         "outcome",
#         do_control={"treatment": 0},
#         do_treat={"treatment": 1},
#     )
#     assert naive_ate == 0.7

#     # god_model = Model(
#     #     MultinomialEstimator(data, prior=0.1),
#     #     Graph([
#     #         v.outcome <= [v.pathway, v.severity],
#     #         v.pathway <= v.treatment,
#     #         v.treatment <= v.severity,
#     #     ])
#     # )
#     # est = god_model.estimand("outcome", do=["treatment"])
#     # print("god interventional", est.to_latex())
#     # print("go", est.__repr__())

#     # god_ate = god_model.ate(
#     #     "outcome",
#     #     do_control={"treatment": 0},
#     #     do_treat={"treatment": 1},
#     # )
#     # assert god_ate == -0.3

#     # smart_model = Model(
#     #     MultinomialEstimator(data, prior=0.1, observed=["outcome", "pathway", "treatment"]),
#     #     Graph([
#     #         v.outcome <= v.pathway,
#     #         v.pathway <= v.treatment,
#     #         v.treatment & v.outcome
#     #     ])
#     # )
#     # # print(df)
#     # # print(smart_model.graph)
#     # # print("estimand", smart_model.estimand("outcome", do=["treatment"]).to_latex())
#     # # print("E[out | do(treat = 1)] = ", smart_model.expectation("outcome", do={"treatment": 1}))
#     # # print("E[out | do(treat = 0)] = ", smart_model.expectation("outcome", do={"treatment": 0}))
#     # smart_ate = smart_model.ate("outcome", do_control={"treatment": 0}, do_treat={"treatment": 1})
#     # assert smart_ate == -0.3


# # def another_test():
# #     df = pd.DataFrame()
# #     df["severity"] = [0, 1]
# #     df["treatment"] = [0, 1]
# #     df["pathway"] = [1, 0]
# #     df["outcome"] = [1, 1]

# #     data = Data(df, {"outcome": "binary"})
