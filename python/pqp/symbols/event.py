from pqp.symbols.variable import Variable
from pqp.symbols.abstract_math import AbstractMath

from abc import ABC, abstractmethod

class Event(AbstractMath, ABC):
    """Abstract base class for events"""
    @property
    @abstractmethod
    def get_var(self):
        """Returns the variable which is constrained by the event"""
        pass

class StatisticalEvent(Event):
    """Abstract base class for events which are statistical events
    
    StatisticalEvents represent constraints on the possible values of a Variable, including 
    taking on a specific value. They go in probability expressions.
    """
    pass

class InterventionEvent(Event):
    """Represents intervening on a variable"""
    def __init__(self, v):
        if not isinstance(v, StatisticalEvent) and not isinstance(v, Variable):
            raise TypeError(f"v must be a Variable or Event, not {type(v)}")
        self.v = v
    
    def get_var(self):
        if isinstance(self.v, Variable):
            return self.v
        else:
            return self.v.get_var()
    
    def __eq__(self, other):
        if not isinstance(other, InterventionEvent):
            return False
        return self.v == other.v
    
    def __repr__(self):
        return f"InterventionEvent({self.v.__repr__()})"
    
    def to_latex(self):
        return "\\text{do}" + f"({self.v.to_latex()})"
    
    def __str__(self):
        return f"do({self.v})"
    
    def assign(self, val):
        if isinstance(self.v, Variable):
            return InterventionEvent(EqualityEvent(self.v, val))
        else:
            raise ValueError(f"Cannot assign to InterventionEvent as subevent already holds: {self.v.__repr__()}")

def do(v):
    """Convenience function for creating an InterventionEvent"""
    return InterventionEvent(v)

class EqualityEvent(StatisticalEvent):
    """Represents setting a variable to a value

    Attributes:
        var (Variable): The variable to set
        val (object): The value to set the variable to (cannot be a Variable)
    """
    def __init__(self, var, val):
        if not isinstance(var, Variable):
            raise TypeError(f"var must be a Variable, not {type(var)}")

        self.var = var
        self.val = val
    
    def get_var(self):
        return self.var
    
    def __eq__(self, other):
        if not isinstance(other, EqualityEvent):
            return False
        return self.var == other.var and self.val == other.val
    
    def __repr__(self):
        return f"EqualityEvent({self.var}, {self.val})"
    
    def __str__(self):
        return f"{self.var} = {self.val}"
    
    def to_latex(self):
        if type(self.val) in [float, int]:
            return f"{self.var.to_latex()} = {self.val}"
        elif isinstance(self.val, Expression):
            return f"{self.var.to_latex()} = {self.val.to_latex()}"
        else:
            return f"{self.var.to_latex()} = {self.val}"
    
    # def r_adapt_map(self, func):
    #     A, B = func(self)
    #     return A(self)