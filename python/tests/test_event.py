from pqp.symbols import *
from pytest import raises

def test_init_errs():
    x, y = make_vars("xy")
    with raises(TypeError):
        do(do(x))
    with raises(TypeError):
        do(EqualityEvent(InterventionEvent, x))
    