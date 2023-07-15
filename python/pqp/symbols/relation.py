import json
from abc import ABC, abstractmethod

from pqp.symbols.variable import Variable
from pqp.symbols.abstract_math import AbstractMath
from pqp.symbols.event import EqualityEvent, Event, InterventionEvent

class AbstractExpression(AbstractMath, ABC):
    """Abstract class defining needed recursive operations for relations"""

    def __eq__(self, other):
        """Returns True if two expressions are structurally equivalent."""
        if not isinstance(other, AbstractExpression):
            return False
        return self.sorted().syntactic_eq(other.sorted())
    
    def __truediv__(self, other):
        """Returns a Quotient of the expressions."""
        if isinstance(other, AbstractExpression):
            return Quotient(self, other)
        else:
            raise TypeError("Cannot divide by non-expression")
    
    def __mul__(self, other):
        """Returns a Product of the expressions."""
        if isinstance(other, AbstractExpression):
            return Product([self, other])
        else:
            raise TypeError("Cannot multiply by non-expression")
    
    def __sub__(self, other):
        """Returns a Difference of the expressions."""
        if isinstance(other, AbstractExpression):
            return Difference(self, other)
        else:
            raise TypeError("Cannot find difference between expression and non-expression")
    
    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def syntactic_eq(self, other):
        """Test whether two Expressions are syntactically identical (structural compare without sorting first)"""
        raise NotImplementedError()
    
    @abstractmethod
    def sorted(self):
        """Returns a sorted copy of an expression for structural comparison."""
        raise NotImplementedError()
    
    @abstractmethod
    def copy(self):
        """Returns a copy of the expression (variables are not copied)."""
        raise NotImplementedError()

    @abstractmethod
    def r_map(self, func):
        """Recursively maps a function over the expression tree"""
        raise NotImplementedError()
    
    @abstractmethod
    def r_adapt_map(self, func):
        """Recursive map where the func decides callables used to transform children

        DO NOT USE! This is a powerful and necessary method but it results in almost unreadable code.

        So, `func` takes an `AbstractExpression` and needs to return a `tuple` of two things. First, 
        a function `A` which maps from `AbstractExpression` to `AbstractExpression`. Second, a function `B` 
        of the same time as `func`.

        At each level of recursion, `func` will be called on an expression `E` to get `A` and `B`.
        This method, `r_adapt_map` will then be called on the children of `E`
        with `B` as input (if `B` is `None`, recursion terminates). An expression of the same 
        type as `E` is then constructed with the results of the recursive calls using `B`, and `A` is
        applied to the result.
        
        Args:
            func (function): A function that takes an AbstractExpression and returns two functions (see desc)
        """
        raise NotImplementedError()
    
    def free_variables(self):
        """Returns the set of free variables in an expression."""
        free = set()
        def func_from_prohibited(prohibited):
            def func(exp):
                if exp.__class__.__name__ == "P":
                    for v in exp._free_variables() - prohibited:
                        free.add(v)
                    return lambda x: x, None
                elif isinstance(exp, _NamespaceModifier):
                    return lambda x: x, func_from_prohibited(prohibited | exp._modified_set())
                else:
                    return lambda x: x, func_from_prohibited(prohibited)
            return func
        self.r_adapt_map(func_from_prohibited(set()))
        return free
    
    def assign(self, var, val=None):
        """Assigns a value to a variable in an expression.

        Note that assignment will not propogate downwards through a sum over a variable.
        
        Args:
            var (Variable): The variable to assign to
            val (AbstractMath): The value to assign, if this is P.unassigned, the expression is copied and returned
        
        Returns:
            AbstractExpression: a new expression where the assignment has occured
        """
        if isinstance(var, dict):
            if val is not None:
                raise ValueError("second argument must be None if passing dict")
            ans = self
            for k, v in var.items():
                ans = ans.assign(k, v)
            return ans
        
        if isinstance(var, str):
            var = Variable(var)
        elif not isinstance(var, Variable):
            raise TypeError(f"first argument must be Variable or dict, not {type(var)}")
        
        if isinstance(val, Variable):
            raise TypeError("second argument must not be a Variable")
        
        from pqp.symbols.p import P
        if val == P.unassigned:
            return self.copy()
        
        def func(exp):
            if isinstance(exp, P):
                return lambda exp: exp._assign(var, val), None
            elif isinstance(exp, _NamespaceModifier) and exp._in_modified(var):
                return lambda x: x.copy(), None
            else:
                return lambda x: x, func
        
        return self.r_adapt_map(func)
    
    def intervene(self, var):
        """Intervenes on a variable in an expression.

        Note that intervention will not propogate downwards through a sum over a variable.
        
        Args:
            var (Variable or list): The variable(s) to intervene on
        
        Returns:
            AbstractExpression: a new expression where the intervention has occured
        """
        if not isinstance(var, Variable):
            try:
                iter(var)
            except TypeError:
                raise ValueError("var must be a Variable or iterable of Variables")
            
            ans = self
            for v in var:
                ans = ans.intervene(v)
            return ans
        
        from pqp.symbols.p import P
        def func(exp):
            if isinstance(exp, P):
                return lambda exp: exp._intervene(var), None
            elif isinstance(exp, _NamespaceModifier) and exp._in_modified(var):
                return lambda x: x.copy(), None
            else:
                return lambda x: x, func
        
        return self.r_adapt_map(func)

class Value(AbstractExpression):
    def __init__(self, var: Variable):
        if not isinstance(var, Variable):
            raise TypeError("var must be a Variable")
        self.var = var
    
    def to_latex(self):
        return self.var.to_latex()
    
    def syntactic_eq(self, other):
        return (
            (isinstance(other, Variable) and (self.var.name == other.name)) or
            (isinstance(other, Value) and (self.var.name == other.var.name))
            )
    
    def sorted(self):
        return self.copy()
    
    def copy(self):
        return Value(self.var)
    
    def r_map(self):
        return func(self)
    
    def r_adapt_map(self, func):
        A, B = func(self)
        return A(self)

class Quotient(AbstractExpression):
    """Represents a quotient of expressions

    Args:
        numer (AbstractExpression): The numerator
        denom (AbstractExpression): The denominator
    """
    def __init__(self, numer, denom):
        if not isinstance(numer, AbstractExpression):
            raise TypeError("numerator must be an instance of AbstractExpression")
        if not isinstance(denom, AbstractExpression):
            raise TypeError("denominator must be an instance of AbstractExpression")
        
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
    
    def copy(self):
        return Quotient(self.numer.copy(), self.denom.copy())
    
    def r_map(self, func):
        return func(Quotient(
            self.numer.r_map(func),
            self.denom.r_map(func),
        ))

    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            return A(Quotient(
                self.numer.r_adapt_map(B),
                self.denom.r_adapt_map(B),
            ))
        else:
            return A(self.copy())

class Product(AbstractExpression):
    """Represents a product of expressions

    Args:
        expr (list of AbstractExpression): The expressions to multiply
    """
    def __init__(self, expr):
        if not isinstance(expr, list):
            expr = list(expr)
        for e in expr:
            if not isinstance(e, AbstractExpression):
                raise TypeError(f"Product must be a list of instances of AbstractExpression, not {type(e)}")
        
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
    
    def copy(self):
        return Product([e.copy() for e in self.expr])
    
    def r_map(self, func):
        return func(Product([e.r_map(func) for e in self.expr]))
    
    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            new_expr = []
            for e in self.expr:
                new_expr.append(e.r_adapt_map(B))
            return A(Product(new_expr))
        else:
            return A(self.copy())

class Difference(AbstractExpression):
    """Represents the difference between two expressions

    Represents the expression $a - b$. Can be creating using the infix operator '-'.
    
    Args:
        a (AbstractExpression): The first expression
        b (AbstractExpression): The second expression
    """
    def __init__(self, a, b):
        if not isinstance(a, AbstractExpression):
            raise TypeError("Difference must be a list of instances of AbstractExpression")
        if not isinstance(b, AbstractExpression):
            raise TypeError("Difference must be a list of instances of AbstractExpression")
        
        self.a = a
        self.b = b
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Difference) and
            self.a == other.a and
            self.b == other.b
        )
    
    def sorted(self):
        return Difference(self.a.sorted(), self.b.sorted())
    
    def __repr__(self):
        return f"Difference({repr(self.a)}, {repr(self.b)})"
    
    def __str__(self):
        return "%s - %s" % (str(self.a), str(self.b))
    
    def to_latex(self):
        return f"{self.a.to_latex()} - {self.b.to_latex()}"
    
    def copy(self):
        return Difference(self.a.copy(), self.b.copy())
    
    def r_map(self, func):
        return func(Difference(
            self.a.r_map(func),
            self.b.r_map(func),
        ))
    
    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            return A(Difference(
                self.a.r_adapt_map(B),
                self.b.r_adapt_map(B),
            ))
        else:
            return A(self.copy())


class _NamespaceModifier(ABC):    
    @abstractmethod
    def _in_modified(self, var):
        raise NotImplementedError()
    
    @abstractmethod
    def _modified_set(self):
        raise NotImplementedError()


class Marginal(AbstractExpression, _NamespaceModifier):
    """Represents a sum

    Args:
        sub (list of Variable): The variables to sum over
        expr (AbstractExpression): The expression to sum
    """
    def __init__(self, sub, expr):
        if not isinstance(expr, AbstractExpression):
            raise TypeError("Marginal must be a list of instances of AbstractExpression")
        if isinstance(sub, Variable):
            sub = [sub]
        elif not isinstance(sub, list):
            sub = list(sub)
        for s in sub:
            if not isinstance(s, Variable):
                raise TypeError("Marginal must be a list of Variables")

        self.sub = sub
        self.expr = expr
    
    def _in_modified(self, var):
        return var in self.sub
    
    def _modified_set(self):
        return set(self.sub)
    
    def sorted(self):
        return Marginal(sorted(self.sub), self.expr.sorted())
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Marginal) and
            self.sub == other.sub and
            self.expr == other.expr
        )
    
    def __repr__(self):
        return f"Marginal({repr(self.sub)}, {repr(self.expr)})"
    
    def __str__(self):
        return "Σ_(%s) [ %s ]" % (", ".join(str(c) for c in self.sub), str(self.expr))
    
    def to_latex(self):
        return (
            "\\sum_{" + ", ".join(c.to_latex() for c in self.sub) + "} \\big(" +
            self.expr.to_latex()
            + "\\big)")
    
    def copy(self):
        return Marginal(self.sub, self.expr.copy())
    
    def r_map(self, func):
        return func(Marginal(
            self.sub,
            self.expr.r_map(func),
        ))
    
    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            return A(Marginal(
                list(self.sub),
                self.expr.r_adapt_map(B),
            ))
        else:
            return A(self.copy())


class Expectation(AbstractExpression, _NamespaceModifier):
    """Represents an expectation or a random variable

    Equivalent to $\sum_{domain(sub)} sub * expr$

    Args:
        sub (Variable): The variable to sum over
        expr (AbstractExpression): The expression to sum
    """
    def __init__(self, sub, expr):
        if not isinstance(expr, AbstractExpression):
            raise TypeError("expr must be a list of instances of AbstractExpression")
        
        if not isinstance(sub, Variable):
            raise TypeError("sub must be a Variable")

        self.sub = sub
        self.expr = expr
    
    def _in_modified(self, var):
        return var == self.sub
    
    def _modified_set(self):
        return {self.sub}
    
    def syntactic_eq(self, other):
        return (
            isinstance(other, Expectation) and
            self.sub == other.sub and
            self.expr == other.expr
        )
    
    def sorted(self):
        return Expectation(self.sub, self.expr.sorted())
    
    def __repr__(self):
        return f"Expectation({repr(self.sub)}, {repr(self.expr)})"
    
    def __str__(self):
        return f"E_({self.sub}) [ {self.expr} ]"
    
    def to_latex(self):
        return "E_{" + self.sub.to_latex() + "} \\big[" + self.expr.to_latex() + "\\big]"
    
    def copy(self):
        return Expectation(self.sub, self.expr.copy())
    
    def r_map(self, func):
        return func(Expectation(
            self.sub,
            self.expr.r_map(func),
        ))
    
    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            return A(Expectation(self.sub, self.expr.r_adapt_map(B)))
        else:
            return A(self.copy())

class Hedge(AbstractExpression):
    """Represents a failure to identify the query"""
    def syntactic_eq(self, other):
        return isinstance(other, Hedge)
    
    def sorted(self):
        return self
    
    def __str__(self):
        return "FAIL"
    
    def to_latex(self):
        return "\\textbf{FAIL}"
    
    def r_map(self, func):
        return func(self)
    
    def r_adapt_map(self, func):
        A, B = func(self)
        return A(self)
    
    def copy(self):
        return Hedge()
    
    def __repr__(self):
        return "FAIL"

def create_literal(name, arity=1, sep=", ", name_tex=None, sep_tex=None):
    """Class factory for creating expression literals

    Suppose you have a function `f` that takes a single expression as an argument and you 
    want to use this function in a symbolic expression.

    >>> F = create_literal("f")
    >>> x = Variable("x")
    >>> F(x)
    f(x)
    >>> F(x).to_latex()
    $f(x)$

    Args:
        name (str): The name of the new class
        arity (int, optional): The arity of the new class. Defaults to 1. Zero is allowed.
        sep (str, optional): The separator to use when printing the expression. Defaults to ", ".
        name_tex (str, optional): The name of the new class in LaTeX. Defaults to name.
        sep_tex (str, optional): The separator to use when printing the expression in LaTeX. Defaults to sep.
    Returns:
        A new subclass of `AbstractExpression`

    """

    # I ❤️ closures
    if name_tex is None:
        name_tex = name
    if sep_tex is None:
        sep_tex = sep

    class NewLiteral(AbstractExpression):
        def __init__(self, *args):
            if len(args) != arity:
                raise ValueError(f"Expected {arity} arguments, got {len(args)}")
            
            for arg in list(args):
                if not isinstance(arg, AbstractMath):
                    raise TypeError(f"Expected {AbstractMath.__name__}, got {type(arg)}")
            
            self.args = args
        
        def __repr__(self):
            if arity == 0:
                return name
            return f"{name}({sep.join(a.__repr__() for a in self.args)})"
        
        def copy(self):
            new_args = tuple(a.copy() for a in self.args)
            return self.__class__(new_args)
        
        def sorted(self):
            def arg_sorter(arg):
                if hasattr(arg, "sorted"):
                    return arg.sorted()
                elif isinstance(arg, Variable):
                    return arg
                else:
                    raise TypeError(f"Cannot sort {arg}")

            new_args = tuple(arg_sorter(a) for a in self.args)
            return self.__class__(*new_args)
        
        def syntactic_eq(self, other):
            def arg_eq(a, b):
                if hasattr(a, "syntactic_eq"):
                    return a.syntactic_eq(b)
                else:
                    return a == b
            
            return (
                (isinstance(other, self.__class__)) and
                (len(self.args) == len(other.args)) and
                all(arg_eq(a, b) for a, b in zip(self.args, other.args))
            )
        
        def r_map(self, func):
            new_args = tuple(args.r_map(func) for args in self.args)
            return func(self.__class__(*new_args))
        
        def r_adapt_map(self, func):
            A, B = func(self)
            if B is not None:
                new_args = [
                    arg.r_adapt_map(B) if hasattr(arg, "r_adapt_map")
                    else arg
                    for arg in self.args
                ]
                return A(self.__class__(*new_args))
            else:
                return A(self.copy())
        
        def free_variables(self):
            def free(obj):
                if hasattr(obj, "free_variables"):
                    return obj.free_variables()
                elif isinstance(obj, Variable):
                    return {obj}
                else:
                    return set()
            return set().union(*(free(arg) for arg in self.args))
        
        def to_latex(self):
            return f"{name_tex}({sep_tex.join(a.to_latex() for a in self.args)})"
    
    NewLiteral.__name__ = name
    return NewLiteral
