from pqp.data.domain import *
import pytest
import numpy as np

def test_make_domain():
    assert isinstance(make_domain("binary"), BinaryDomain)
    assert isinstance(make_domain("discrete", [1, 2, 3]), CategoricalDomain)
    assert isinstance(make_domain("continuous", [1, 2, 3]), RealDomain)

    with pytest.raises(ValueError):
        make_domain("invalid")
    
    with pytest.raises(ValueError):
        make_domain("discrete")
    
    with pytest.raises(ValueError):
        make_domain("continuous")


def test_domain_membership():
    d = make_domain("discrete", [1, 2, 3])
    assert 1 in d
    assert 8 not in d

    c = make_domain("continuous", [1, 2, 3])
    assert 1.5 in c
    assert 8 not in c
    assert 1 in c

    i = make_domain("integer", [1, 2, 3])
    assert 1 in i
    assert 1.5 not in i
    assert 8 not in i

def test_infer_domain_type():
    assert infer_domain_type(np.array([True, False])) == "binary"
    assert infer_domain_type(np.array([0, 1])) == "binary"
    assert infer_domain_type(np.array([1, 2])) == "integer"
    assert infer_domain_type(np.array([1.0, 2.0, 3.0])) == "continuous"
    assert infer_domain_type(np.array(["foo"])) == "discrete"

    assert infer_domain_type([True, False]) == "binary"
    assert infer_domain_type([0, 1]) == "binary"
    assert infer_domain_type([1, True]) == "binary"
    assert infer_domain_type([True, 2]) == "integer"
    assert infer_domain_type([1, 2]) == "integer"
    assert infer_domain_type([1.0, 2.0, 3.0]) == "integer"
    assert infer_domain_type([1.5, 2.0, 3.0]) == "continuous"
    assert infer_domain_type(["foo"]) == "discrete"

    with pytest.raises(TypeError):
        infer_domain_type(1)

