from pqp.symbols import *

def test_r_map():
    x, y, z = make_vars(["x", "y", "z"])
    px_y = P([x], given=[y])
    assert px_y.r_map(lambda e: e) == px_y
    assert Product([px_y, px_y]).r_map(lambda e: e) == Product([px_y, px_y])
    assert Marginal([x], px_y).r_map(lambda e: e) == Marginal([x], px_y)
    assert Quotient(px_y, px_y).r_map(lambda e: e) == Quotient(px_y, px_y)
    assert Difference(px_y, px_y).r_map(lambda e: e) == Difference(px_y, px_y)
    assert Expectation(x, px_y).r_map(lambda e: e) == Expectation(x, px_y)

def test_assign():
    # tests whether the assignment method works on increasingly complicated expressions

    x, y, z = make_vars(["x", "y", "z"])

    # test assignment inside a conditional probability
    assert P(x)._assign(x, 3) == P(EqualityEvent(x, 3))
    assert P(x).assign(x, 3) == P(EqualityEvent(x, 3))
    assert P([x], given=[y]).assign(x, 3) == P([EqualityEvent(x, 3)], given=[y])
    assert P([x], given=[y]).assign(x, 3).assign(y, 4) == P([EqualityEvent(x, 3)], given=[EqualityEvent(y, 4)])
    assert (P(x) * P(y)).assign(x, 5) == P(EqualityEvent(x, 5)) * P(y)
    assert (P(x) * P(y)).assign({x: 5}) == P(EqualityEvent(x, 5)) * P(y)

def test_assign_past_failed():
    x, y = make_vars(["x", "y"])
    assert Expectation(x, P(x, given=y)).assign({"x": 1, "y": 1}) ==\
        Expectation(x, P(x, given=y.val==1))
    assert (Expectation(x, P(x, given=y)) * P(y)).assign({"x": 1, "y": 1}) ==\
        (Expectation(x, P(x, given=y.val==1)) * P(y.val==1))

def test_assign_marginal_namespacing():
    x, y, z = make_vars(["x", "y", "z"])

    exp = Marginal([x], P([x], given=[y]))
    assert exp.assign(x, 3) == exp

    exp = Marginal([y], P(x) * Marginal([x], P([x], given=z)))
    after = Marginal(y, P(x.val == 3) * Marginal([x], P([x], given=z)))
    assert exp.assign(x, 3) == after

    exp = Expectation(x, P([x], given=[y]))
    assert exp.assign(x, 3) == exp

    exp = Expectation(y, P(x) * Expectation(x, P([x], given=z)))
    after = Expectation(y, P(x.val == 3) * Expectation(x, P([x], given=z)))
    assert exp.assign(x, 3) == after
