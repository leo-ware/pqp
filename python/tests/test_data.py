from pqp.data.data import Data
from pqp.utils.exceptions import DomainValidationError
from pqp.data.domain import RealDomain, CategoricalDomain, BinaryDomain, IntegerDomain
from pqp.symbols.variable import Variable
from pqp.estimation import MultinomialEstimator

import pytest
import pandas as pd

def test_data_domains():
    df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
    data = Data(df, {"x": "continuous", "y": "binary"})

    assert isinstance(data.vars.x.domain, RealDomain)
    assert data.vars.x.domain.get_cardinality() == float("inf")
    assert data.vars.x.domain.min == 0
    assert data.vars.x.domain.max == 2

    assert isinstance(data.vars.y.domain, CategoricalDomain)
    assert isinstance(data.vars.y.domain, BinaryDomain)
    assert data.vars.y.domain.get_cardinality() == 2

def test_tricky_data_inits():
    df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})

    assert Data(df, {"x": Variable("X"), "y": "binary"}, silence_inferred_domain_warning=True)
    assert Data(df, {"x": "binary", "y": Variable("Y")}, validate_domain=False, silence_inferred_domain_warning=True)
    assert Data(df, [Variable("x"), Variable("y")], silence_inferred_domain_warning=True)
    assert Data(df)

    with pytest.raises(ValueError):
        Data(df, [Variable("x"), Variable("z")], silence_inferred_domain_warning=True)
    with pytest.raises(ValueError):
        Data(df, [Variable("x"), Variable("y"), Variable("z")], silence_inferred_domain_warning=True)
    with pytest.raises(TypeError):
        Data(df, [None], silence_inferred_domain_warning=True)

def test_data_infer_domain():
    df = pd.DataFrame({"i": [0, 1, 2], "b": [0, 1, 0], "c": [1.1, 2, 3], "d": ["foo", 2, 3]})
    data = Data(df)

    assert isinstance(data.vars.i.domain, IntegerDomain)
    assert isinstance(data.vars.b.domain, BinaryDomain)
    assert isinstance(data.vars.c.domain, RealDomain)
    assert isinstance(data.vars.d.domain, CategoricalDomain)

def test_domain_validation():
    df = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(DomainValidationError):
        Data(df, {"x": "binary"})
    
    df = pd.DataFrame({"x": [0, 1, 1.5]})
    with pytest.raises(DomainValidationError):
        Data(df, {"x": "integer"})

    df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 1.5]})
    with pytest.raises(DomainValidationError):
        Data(df, {"x": "binary", "y": "discrete"})
    with pytest.raises(DomainValidationError):
        Data(df, {"x": "continuous", "y": "integer"})

def test_quantize():
    df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
    data = Data(df, {"x": "continuous", "y": "binary"})
    data.quantize("x")
    assert isinstance(data.domain_of("x"), CategoricalDomain)
    assert data.domain_of("x").get_cardinality() == 2

    df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
    data = Data(df, {"x": "continuous", "y": "binary"})
    MultinomialEstimator(data)
    assert isinstance(data.domain_of("x"), CategoricalDomain)
    assert data.domain_of("x").get_cardinality() == 2
