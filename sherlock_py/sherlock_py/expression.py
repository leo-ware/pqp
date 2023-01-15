from IPython.display import display, Math
import json

def parse_json(exp):
    """Parses JSON returned from backend.id() into an Expression object.

    Args:
        exp (str or dict): The JSON string or parsed JSON object.
    
    Returns:
        Expression: The parsed expression.
    """
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
    """Base class for all expressions."""
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def display(self):
        """Renders an expression as Latex using IPython.display"""
        return display(Math(self.to_latex()))
    
    def to_latex(self):
        """Returns the Latex representation of an expression."""
        raise NotImplementedError()

class Variable(Expression):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def to_latex(self):
        return self.name

class Quotient(Expression):
    def __init__(self, numer, denom):
        self.numer = numer
        self.denom = denom
    
    def __str__(self):
        return "[%s / %s]" % (str(self.numer), str(self.denom))
    
    def to_latex(self):
        return "{" + self.numer.to_latex() + " \over " + self.denom.to_latex() + "}"

class Product(Expression):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return " * ".join([str(e) for e in self.expr])
    
    def to_latex(self):
        return " ".join([e.to_latex() for e in self.expr])

class Marginal(Expression):
    def __init__(self, sub, expr):
        self.sub = sub
        self.expr = expr
    
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