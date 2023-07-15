from pqp.identification.estimands import ATE, CATE
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

def test_literal():
    x, y, z = make_vars("xyz")
    ate_lit = ATE(y, treatment_condition={x: 1}, control_condition={x: 0}).literal()
    assert ate_lit.to_latex() == "\\text{ATE}(y \\mid x)"
    cate_lit = CATE(y, control_condition={x: 0}, treatment_condition={x: 1}, subpopulation={z: 1}).literal()
    assert cate_lit.to_latex() == "\\text{CATE}(y \\mid x \\mid z)"