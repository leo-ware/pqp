# from pqp.robustness.abstract_step import AbstractStep, Assumption

# def test_abstract_step():
#     class Step(AbstractStep):
#         def __init__(self):
#             super().__init__("Step")
    
#     step = Step()
#     assert step.assumptions == []
#     step.assume("foo")
#     assert step.assumptions[0].name == "foo"
#     res = step.result(foo=1, bar=2)
#     assert res.foo == 1
#     assert res.bar == 2
#     assert res.assumptions[0].name == "foo"
#     assert res.backref is step
#     assert res.__class__.__name__ == "StepResult"
