import json

def parse_json(exp):
    """Parses JSON returned from backend.id() into an Expression object.

    Args:
        exp (str or dict): The JSON string or parsed JSON object.
    
    Returns:
        Expression: The parsed expression.
    """
    from pqp.variable import Variable

    if isinstance(exp, str):
        return parse_json(json.loads(exp))

    if exp["type"] == "Quotient":
        return Quotient(
            parse_json(exp["numer"]),
            parse_json(exp["denom"]),
        )
    elif exp["type"] == "Product":
        return Product(
            [parse_json(e) for e in exp["exprs"]],
        )
    elif exp["type"] == "Marginal":
        return Marginal(
            [Variable(x) for x in exp["sub"]],
            parse_json(exp["exp"]),
        )
    elif exp["type"] == "Hedge":
        return Hedge()
    elif exp["type"] == "P":
        return P(
            [Variable(e) for e in exp["vars"]],
            [Variable(e) for e in exp["given"]],
        )
    else:
        raise Exception("Unknown expression type: " + exp["type"])

class Expression:
    """Base class for all expressions.
    
    The primary use of Expression is to represent the results of identification. However,
    Expressions can be constructed from Variables and other Expressions. Using the
    infix `/` and `*` operators.

    Examples:
        >>> from pqp.variable import make_vars
        >>> x, y = make_vars("xy")
        >>> x / y
        Quotient(Variable(x), Variable(y))
        >>> x * y
        Product([Variable(x), Variable(y)])
    
    Expressions can be represented in a number of different ways.
        - `__repr__` returns an unambiguous representation of the expression
        - `__str__` returns a human-readable (ascii, symbolic) representation
        - `to_latex` returns a Latex representation of the expression
    
    """

    def display(self):
        """Renders an expression as Latex using IPython.display"""
        from IPython.display import display, Math
        return display(Math(self.to_latex()))
    
    def to_latex(self):
        """Returns the Latex representation of an expression."""
        raise NotImplementedError()
    
    def __truediv__(self, other):
        if isinstance(other, Expression):
            return Quotient(self, other)
        else:
            raise TypeError("Cannot divide by non-expression")
    
    def __mul__(self, other):
        if isinstance(other, Expression):
            return Product([self, other])
        else:
            raise TypeError("Cannot multiply by non-expression")

class Quotient(Expression):
    def __init__(self, numer, denom):
        self.numer = numer
        self.denom = denom
    
    def __repr__(self):
        return f"Quotient({repr(self.numer)}, {repr(self.denom)})"
    
    def __str__(self):
        return "[%s / %s]" % (str(self.numer), str(self.denom))
    
    def to_latex(self):
        return "{" + self.numer.to_latex() + " \over " + self.denom.to_latex() + "}"

class Product(Expression):
    def __init__(self, expr):
        self.expr = expr
    
    def __repr__(self):
        return f"Product({[repr(e) for e in self.expr]})"
    
    def __str__(self):
        return " * ".join([str(e) for e in self.expr])
    
    def to_latex(self):
        return " ".join([e.to_latex() for e in self.expr])

class Marginal(Expression):
    def __init__(self, sub, expr):
        self.sub = sub
        self.expr = expr
    
    def __repr__(self):
        return f"Marginal({self.sub}, {repr(self.expr)})"
    
    def __str__(self):
        return "Σ_(%s) [ %s ]" % (", ".join(str(c) for c in self.sub), str(self.expr))
    
    def to_latex(self):
        return (
            "\\sum_{" + ", ".join(c.to_latex() for c in self.sub) + "} \\big(" +
            self.expr.to_latex()
            + "\\big)")

class P(Expression):
    def __init__(self, vars, given):
        self.vars = vars
        self.given = given
    
    def __str__(self):
        v = ", ".join(str(c) for c in self.vars)
        g = ", ".join(str(c) for c in self.given)
        if not v:
            return "1"
        return "P(" + v + (f"| {g}" if g else "") + ")"
    
    def __repr__(self):
        if self.given:
            return f"P({self.vars} | {self.given})"
        else:
            return f"P({self.vars})"
    
    def to_latex(self):
        v = ", ".join(c.to_latex() for c in self.vars)
        g = ", ".join(c.to_latex() for c in self.given)
        if not v:
            return "1"
        return "P(" + v + (f" \\mid {g}" if g else "") + ")"

class Hedge(Expression):
    """Represents a failure to identify the query"""
    def __str__(self):
        return "FAIL"
    
    def to_latex(self):
        return "\\textbf{FAIL}"