from pqp.symbols.abstract_math import AbstractMath
from pqp.data.domain import Domain
from pqp.utils.exceptions import DomainValidationError

import numpy as np
import pandas as pd


class _VarEventInfixProvider:
    def __init__(self, var):
        self.var = var
    
    def __eq__(self, val):
        from pqp.symbols.event import EqualityEvent
        if isinstance(val, (Variable, _VarEventInfixProvider)):
            raise ValueError("EqualityEvent is not for use between two variables")
        return EqualityEvent(self.var, val)


class Variable(AbstractMath):
    """A variable in the causal model
    
    Dunder methods allow for convenient syntax for creating causal graphs.

    Example:
        >>> x = Variable("x")
        >>> y = Variable("y")
        >>> x <= y
        DirectedEdge(Variable("x"), Variable("y"))
        >>> x & y
        BidirectedEdge(Variable("x"), Variable("y"))
    
    Args:
        name (str): the name of the variable
    """
    def __init__(self, name, domain=None):
        if type(name) != str:
            raise TypeError(f"name must be a string, not {type(name)}")
        
        self.name = name
        self.val = _VarEventInfixProvider(self)

        if domain is None or isinstance(domain, Domain):
            self.domain = domain
        elif isinstance(domain, str):
            self.domain = make_domain(domain)
        else:
            raise TypeError(f"domain must be a Domain, string, or None, not {type(domain)}")
    
    def __repr__(self):
        return f"Variable({self.name})"
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __le__(self, other):
        from pqp.identification.graph import DirectedEdge, BidirectedEdge
        if isinstance(other, Variable):
            return DirectedEdge(other, self)
        elif isinstance(other, DirectedEdge):
            return self <= other.end
        elif isinstance(other, BidirectedEdge):
            return self <= other.a
        elif isinstance(other, list):
            return [self <= v for v in other]
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
    
    def __and__(self, other):
        from pqp.identification.graph import BidirectedEdge, DirectedEdge
        if isinstance(other, Variable):
            return BidirectedEdge(self, other)
        elif isinstance(other, BidirectedEdge):
            return self & other.a
        elif isinstance(other, DirectedEdge):
            return self & other.end
        elif isinstance(other, list):
            return [self & v for v in other]
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
    
    def to_latex(self):
        return self.name
    
    # def r_adapt_map(self, func):
    #     A, B = func(self)
    #     return A(self)


def make_vars(names):
    """Creates a list of variables from a list of names
    
    Example:
        >>> make_vars(["x", "y", "z"])
        [Variable("x"), Variable("y"), Variable("z")]
        >>> x, y, z = make_vars("xyz")
        [Variable("x"), Variable("y"), Variable("z")]
    
    """
    return [Variable(name) for name in names]
