from pqp.causal.estimands import ATE, CATE
from pqp.symbols import *

def test_expression():
    x, y, z = make_vars("xyz")
    assert ATE(y, treatment_condition={x: 1}, control_condition={x: 0}).expression() == \
        (Expectation(y, P(y, given=do(x.val == 1))) - Expectation(y, P(y, given=[do(x.val == 0)])))
    assert CATE(y, control_condition={x: 0}, treatment_condition={x: 1}, subpopulation={z: 1}).expression() == \
        (
            Expectation(y, P(y, given=[do(x.val == 1), z.val == 1])) -
            Expectation(y, P(y, given=[do(x.val == 0), z.val == 1]))
        )