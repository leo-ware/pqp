from pqp.symbols import *
from pytest import raises

def test_init():
    x, y, z = make_vars("xyz")
    assert P(x, given=[do(x)])
    assert P(x, given=[y])
    assert P(x, given=[do(z), y])
    assert P(x, given=y.val == 5) == P(x, given=[EqualityEvent(y, 5)])
    assert P(x, given=do(y)) == P(x, given=[do(y)])
    assert P(x, given=do(y.val == 5)) == P(x, given=[do(EqualityEvent(y, 5))])

def test_init_errs():
    x, y = make_vars("xy")
    with raises(ValueError):
        P([x, x])
    with raises(ValueError):
        P(x, given=[x, y])
    with raises(ValueError):
        assert P(do(EqualityEvent(x, 10)))
    with raises(ValueError):
        assert P(do(x))
    with raises(ValueError):
        assert P(do(EqualityEvent(x, 10)))
    with raises(ValueError):
        assert P(do(x), given=[do(y)])

def test_get_vars():
    x, y, z = make_vars(["x", "y", "z"])
    p = P(x, given=y)
    assert p.get_vars() == {x: P.unassigned}
    assert p.get_intervened_vars() == {}
    assert p.get_conditioned_vars() == {y: P.unassigned}

    p = P(x, given=[EqualityEvent(y, 10)])
    assert p.get_vars() == {x: P.unassigned}
    assert p.get_intervened_vars() == {}
    assert p.get_conditioned_vars() == {y: 10}

    p = P(EqualityEvent(x, 15), given=[do(y), do(EqualityEvent(z, 10))])
    assert p.get_vars() == {x: 15}
    assert p.get_intervened_vars() == {y: P.unassigned, z: 10}
    assert p.get_conditioned_vars() == {}

    p = P([x, y], given=[do(z)])
    assert p.get_vars() == {x: P.unassigned, y: P.unassigned}
    assert p.get_intervened_vars() == {z: P.unassigned}
    assert p.get_conditioned_vars() == {}


def test_assign():
    x, y = make_vars("xy")
    p = P(x, given=y)
    assert p._assign(x, 10) == P(EqualityEvent(x, 10), given=y)
    assert p._assign(y, 10) == P(x, given=EqualityEvent(y, 10))

    p = P(x, given=[do(y)])
    assert p._assign(x, 10) == P(EqualityEvent(x, 10), given=[do(y)])
    assert p._assign(y, 10) == P(x, given=[do(EqualityEvent(y, 10))])

def test_intervene():
    x, y, z = make_vars("xyz")
    p = P(x, given=y)
    assert p._intervene(x) == P(x, given=[y]) # this seems unwise, but not sure what else to do
    assert p._intervene(y) == P(x, given=[do(y)])
    p = P(x, given=[y, z])
    assert p._intervene(x) == P(x, given=[y, z])
    assert p._intervene(y) == P(x, given=[do(y), z])
    assert p.intervene(y)._intervene(z) == P(x, given=[do(y), do(z)])