from pqp.symbols.relation import AbstractExpression
from pqp.symbols.variable import Variable
from pqp.symbols.event import Event, InterventionEvent, EqualityEvent, do
from pqp.utils import staticproperty

class P(AbstractExpression):
    """Expression representing a probability or conditional probability

    Args:
        vars (list of Variable): probability variables
        given (list of Variable): conditioned variables
    
    Raises:
        ValueError: if a variable is repeated in vars or given
        TypeError: if vars or given are not a list of Variable or Event
    """
    _unassigned = object()

    def __init__(self, vars, given=None):
        if isinstance(vars, Variable) or isinstance(vars, Event):
            vars = [vars]
        elif not isinstance(vars, list):
            vars = list(vars)
        for v in vars:
            if not isinstance(v, Variable) and not isinstance(v, Event):
                raise TypeError("vars must be a list of (Variable | Event)")
            if isinstance(v, InterventionEvent):
                raise ValueError("InterventionEvent not allowed in vars")
        
        if given is not None:
            t = type(given)
            f = isinstance(given, Event)
            if isinstance(given, Variable) or isinstance(given, Event):
                given = [given]
            elif not isinstance(given, list):
                given = list(given)
            for g in given:
                if not (isinstance(g, Variable) or isinstance(g, Event)):
                    raise TypeError("given must be a list of (Variable | Event)")
        
        _present = set()
        for v in (vars or []) + (given or []):
            if isinstance(v, Variable):
                if v in _present:
                    raise ValueError(f"Duplicate variable {v}")
                _present.add(v)
            elif isinstance(v, EqualityEvent):
                if v.get_var() in _present:
                    raise ValueError(f"Duplicate variable {v}")
                _present.add(v.get_var())
        
        self.vars = vars
        self.given = given or []
    
    @staticproperty
    @staticmethod
    def unassigned():
        """Special object marker for unassigned variables, used in certain routines"""
        return P._unassigned
    
    def sorted(self):
        return P(
            sorted(self.vars, key=str),
            sorted(self.given, key=str)
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
            return f"P({self.vars}, given={self.given})"
        else:
            return f"P({self.vars})"
    
    def to_latex(self):
        v = ", ".join(c.to_latex() for c in self.vars)
        g = ", ".join(c.to_latex() for c in self.given)
        if not v:
            return "1"
        return "P(" + v + (f" \\mid {g}" if g else "") + ")"
    
    def copy(self):
        return P(list(self.vars), given=list(self.given))
    
    def r_map(self, func):
        return func(self)
    
    def r_adapt_map(self, func):
        A, B = func(self)
        if B is not None:
            return A(self.copy())
        else:
            return A(self)
    
    def get_vars(self):
        """Get the set of variables to the left of the conditioning bar in this P
        
        Returns:
            set of Variable
        
        Raises:
            TypeError: if self.vars contains an element which is neither Variable nor EqualityEvent
        """
        s = {}
        for v in self.vars:
            if isinstance(v, Variable):
                s[v] = P.unassigned
            elif isinstance(v, EqualityEvent):
                s[v.get_var()] = v.val
            else:
                raise TypeError("encountered element of self.vars which is neither Variable nor EqualityEvent")
        return s
    
    def get_intervened_vars(self):
        """Get the set of variables which are intervened on in this P
        
        Returns:
            dict of Variable -> value
        
        Raises:
            TypeError: if self.given contains an InterventionEvent which contains neither Variable nor EqualityEvent
        """
        s = {}
        for v in self.given:
            if isinstance(v, InterventionEvent):
                if isinstance(v.v, Variable):
                    s[v.v] = P.unassigned
                elif isinstance(v.v, EqualityEvent):
                    s[v.v.get_var()] = v.v.val
                else:
                    raise TypeError("encountered contents of InterventionEvent which is neither Variable nor EqualityEvent")
        return s
    
    def get_conditioned_vars(self):
        """Get the set of variables which are conditioned on in this P

        Raises:
            TypeError: if self.given contains an element which is not Variable, EqualityEvent or InterventionEvent
        
        Returns:
            dict of Variable -> value
        """
        s = {}
        for v in self.given:
            if not isinstance(v, InterventionEvent):
                if isinstance(v, Variable):
                    s[v] = P.unassigned
                elif isinstance(v, EqualityEvent):
                    s[v.get_var()] = v.val
                else:
                    raise TypeError("encountered element of self.given which is neither Variable nor EqualityEvent")
        return s
    
    def _assign(self, var, val):
        """Conditions on a variable assignment, returning a new P"""
        if not isinstance(var, Variable):
            raise TypeError("var must be a Variable")

        vars = [EqualityEvent(var, val) if isinstance(x, Variable) and (var.name == x.name) else x for x in self.vars]
        given = []
        for v in self.given:
            if isinstance(v, Event) and v.get_var() == var:
                if isinstance(v, InterventionEvent):
                    given.append(v.assign(val))
                else:
                    raise ValueError(f"cannot set {var.__repr__()} to {val.__repr__()} as var is already under the following constraint: {v.__repr__()}")
            elif isinstance(v, Variable) and v == var:
                given.append(EqualityEvent(var, val))
            else:
                given.append(v)
        
        return P(vars, given)
    
    def _intervene(self, var):
        """Intervenes on a variable's appearances or assignment behind the conditioning bar, returning a new P"""
        given = []
        for v in self.given:
            if isinstance(v, Variable):
                this_var = v
            elif not isinstance(v, InterventionEvent):
                this_var = v.get_var()
            else:
                this_var = object()
            
            if this_var == var:
                given.append(do(v))
            else:
                given.append(v)
        
        return P(self.vars, given)
    
    def _free_variables(self):
        """Get the set of variables which are free in this P"""
        free = set()
        for g in self.vars + self.given:
            if isinstance(g, Variable):
                free.add(g)
            elif isinstance(g, InterventionEvent) and isinstance(g.v, Variable):
                free.add(g.v)
        return free
