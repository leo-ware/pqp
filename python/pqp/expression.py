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
    
    def syntactic_eq(self, other):
        """Test whether two Expressions are syntactically identical (structural compare without sorting first)"""
        raise NotImplementedError()
    
    def sorted(self):
        """Returns a sorted copy of an expression for structural comparison."""
        raise NotImplementedError()
    
    def __eq__(self, other):
        """Returns True if two expressions are structurally equivalent."""
        if not isinstance(other, Expression):
            return False
        return self.sorted().syntactic_eq(other.sorted())
    
    def to_latex(self):
        """Returns the Latex representation of an expression."""
        raise NotImplementedError()
    
    def __truediv__(self, other):
        """Returns a Quotient of the expressions."""
        if isinstance(other, Expression):
            return Quotient(self, other)
        else:
            raise TypeError("Cannot divide by non-expression")
    
    def __mul__(self, other):
        """Returns a Product of the expressions."""
        if isinstance(other, Expression):
            return Product([self, other])
        else:
            raise TypeError("Cannot multiply by non-expression")

class Quotient(Expression):
    def __init__(self, numer, denom):
        if not isinstance(numer, Expression):
            raise TypeError("numerator must be an Expression")
        if not isinstance(denom, Expression):
            raise TypeError("denominator must be an Expression")
        
        self.numer = numer
        self.denom = denom
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Quotient) and
            self.numer == other.numer and
            self.denom == other.denom
        )
    
    def sorted(self):
        return Quotient(self.numer.sorted(), self.denom.sorted())
    
    def __repr__(self):
        return f"Quotient({repr(self.numer)}, {repr(self.denom)})"
    
    def __str__(self):
        return "[%s / %s]" % (str(self.numer), str(self.denom))
    
    def to_latex(self):
        return "{" + self.numer.to_latex() + " \\over " + self.denom.to_latex() + "}"

class Product(Expression):
    def __init__(self, expr):
        if not isinstance(expr, list):
            expr = list(expr)
        for e in expr:
            if not isinstance(e, Expression):
                raise TypeError("Product must be a list of Expressions")
        
        self.expr = expr
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Product) and
            self.expr == other.expr
        )
    
    def sorted(self):
        return Product(sorted([e.sorted() for e in self.expr], key=str))
    
    def __repr__(self):
        return f"Product({[repr(e) for e in self.expr]})"
    
    def __str__(self):
        return " * ".join([str(e) for e in self.expr])
    
    def to_latex(self):
        return " ".join([e.to_latex() for e in self.expr])

class Marginal(Expression):
    def __init__(self, sub, expr):
        from pqp.variable import Variable

        if not isinstance(expr, Expression):
            raise TypeError("Marginal must be a list of Expressions")
        if isinstance(sub, Variable):
            sub = [sub]
        elif not isinstance(sub, list):
            sub = list(sub)
        for s in sub:
            if not isinstance(s, Variable):
                raise TypeError("Marginal must be a list of Variables")

        self.sub = sub
        self.expr = expr
    
    def sorted(self):
        return Marginal(sorted(self.sub), self.expr.sorted())
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Marginal) and
            self.sub == other.sub and
            self.expr == other.expr
        )
    
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
    def __init__(self, vars, given=None):
        from pqp.variable import Variable

        if not isinstance(vars, list):
            vars = list(vars)
        for v in vars:
            if not isinstance(v, Variable):
                raise TypeError("vars must be a list of Variables")
        
        if given is not None:
            if not isinstance(given, list):
                given = list(given)
            for g in given:
                if not isinstance(g, Variable):
                    raise TypeError("given must be a list of Variables")
        
        self.vars = vars
        self.given = given or []
    
    def sorted(self):
        return P(
            sorted(self.vars, key=lambda v: v.name),
            sorted(self.given, key=lambda v: v.name)
            )
    
    def __str__(self):
        v = ", ".join(str(c) for c in self.vars)
        g = ", ".join(str(c) for c in self.given)
        if not v:
            return "1"
        return "P(" + v + (f"| {g}" if g else "") + ")"
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, P) and
            self.vars == other.vars and
            self.given == other.given
        )
    
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
    def syntactic_eq(self, other):
        return isinstance(other, Hedge)
    
    def sorted(self):
        return self
    
    def __str__(self):
        return "FAIL"
    
    def to_latex(self):
        return "\\textbf{FAIL}"