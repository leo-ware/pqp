from IPython.display import display, Math
import json

def parse_json(exp):
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
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def display(self):
        return display(Math(self.tex()))

class Variable(Expression):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def tex(self):
        return self.name

class Quotient(Expression):
    def __init__(self, numer, denom):
        self.numer = numer
        self.denom = denom
    
    def __str__(self):
        return "[%s / %s]" % (str(self.numer), str(self.denom))
    
    def tex(self):
        return "{" + self.numer.tex() + " \over " + self.denom.tex() + "}"

class Product(Expression):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return " * ".join([str(e) for e in self.expr])
    
    def tex(self):
        return " ".join([e.tex() for e in self.expr])

class Marginal(Expression):
    def __init__(self, sub, expr):
        self.sub = sub
        self.expr = expr
    
    def __str__(self):
        return "Σ_(%s) [ %s ]" % (", ".join(str(c) for c in self.sub), str(self.expr))
    
    def tex(self):
        return (
            "\\sum_{" + ", ".join(c.tex() for c in self.sub) + "} \\big(" +
            self.expr.tex()
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
    
    def tex(self):
        v = ", ".join(c.tex() for c in self.vars)
        g = ", ".join(c.tex() for c in self.given)
        if not v:
            return "1"
        return "P(" + v + (f" \\mid {g}" if g else "") + ")"

class Hedge(Expression):
    def __str__(self):
        return "FAIL"
    
    def tex(self):
        return "FAIL"