from pqp.expression import Expression

class Variable(Expression):
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
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Variable({self.name})"
    
    def __str__(self):
        return self.name
    
    def __le__(self, other):
        from pqp.graph import DirectedEdge
        if isinstance(other, Variable):
            return DirectedEdge(other, self)
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
    
    def __and__(self, other):
        from pqp.graph import BidirectedEdge
        if isinstance(other, Variable):
            return BidirectedEdge(self, other)
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
    
    def to_latex(self):
        return self.name

def make_vars(names):
    """Creates a list of variables from a list of names
    
    Example:
        >>> make_vars(["x", "y", "z"])
        [Variable("x"), Variable("y"), Variable("z")]
        >>> x, y, z = make_vars("xyz")
        [Variable("x"), Variable("y"), Variable("z")]
    
    """
    return [Variable(name) for name in names]