import numpy as np
import pandas as pd

from pqp.estimation.model import Model
from pqp.causal.graph import Graph
from pqp.causal.estimands import ATE
from pqp.data.data import Data
from pqp.parametric.categorical_distribution import CategoricalDistribution, Distribution
from pqp.symbols import *

# def test_direct_effect_estimation():
#     x, y = make_vars("xy")
#     data = Data(pd.DataFrame({
#         "x": [0, 0, 1, 1],
#         "y": [0, 1, 0, 1],
#     }))

#     parametric_model = CategoricalDistribution(data)
#     causal_model = Graph([y <= x])
#     causal_estimand = ATE(y, treatment_condition={x: 1}, control_condition={x: 0})

#     identified_estimand = causal_model.identify(causal_estimand)
#     print(identified_estimand)
#     effect = parametric_model.approx(identified_estimand)
#     print(effect)

#     assert False



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
#         CategoricalDistribution(data, prior=0, observed=["outcome", "treatment"]),
#         Graph([v.outcome <= v.treatment])
#         )
#     naive_ate = naive_model.ate(
#         "outcome",
#         do_control={"treatment": 0},
#         do_treat={"treatment": 1},
#     )
#     assert naive_ate == 0.7

#     # god_model = Model(
#     #     CategoricalDistribution(data, prior=0.1),
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
#     #     CategoricalDistribution(data, prior=0.1, observed=["outcome", "pathway", "treatment"]),
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
