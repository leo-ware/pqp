from pqp.symbols import *
from abc import ABC, abstractmethod
from pqp.data.domain import BinaryDomain

class AbstractCausalEstimand:
    """Abstract base class for causal estimands"""
    def __init__(self):
        self.name = "causal estimand"
    
    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def expression(self):
        """Derive the expression for the causal estimand
        
        Returns:
            AbstractExpression: the expression for the causal estimand
        """
        raise NotImplementedError()
    
    @abstractmethod
    def literal(self):
        """The estimand represented as a function call, as an Expression
        
        Returns:
            AbstractExpression: the literal for the causal estimand
        """
        raise NotImplementedError()
    
    def display(self):
        """Display the causal estimand"""
        from IPython.display import display, Math
        tex = self.literal().to_latex() + " = " + self.expression().to_latex()
        return display(Math(tex))

class CausalEstimand(AbstractCausalEstimand):
    """Subclass of AbstractCausalEstimand which carries its expression as a literal"""
    LITERAL_CLASS = create_literal("CausalEstimand")

    def __init__(self, exp):
        super().__init__()
        self.exp = exp
    
    def __repr__(self):
        return f"CausalEstimand({repr(self.exp)[:12]})"
    
    def expression(self):
        return self.exp
    
    def literal(self):
        return self.__class__.LITERAL_CLASS(self.exp)

class ATE(AbstractCausalEstimand):
    """Causal estimand for the average treatment effect

    To define the average treatment effect, it's necessary to specify what is meant
    by "treatment" and "control" in this context. You can do this by passing either
    a dict or a list of StatisticalEvent objects to each of the treatment_condition
    and control_condition arguments. If a dict is passed, the keys must be Variable
    or string, and the values must not be Variable. If a list is passed, it must 
    contain only instances of StatisticalEvent.

    Example:
        >>> # treatment condition is x = 1, control condition is x = 0 in both of these
        >>> ATE(outcome, treatment_condition={"x": 1}, control_condition={"x": 0})
        >>> ATE(outcome, treatment_condition=[EqualityEvent("x", 1)], control_condition=[EqualityEvent("x", 0)])
        >>>
        >>> # treatment condition is x = 1 and y = "red", control condition is x = 0 and y = "blue"
        >>> ATE(outcome, treatment_condition={"x": 1, y: "red"}, control_condition={"x": 0, y: "blue"})
        
    
    Args:
        outcome (Variable): the outcome variable
        treatment_condition (dict or list): the treatment condition
        control_condition (dict or list): the control condition
    """
    LITERAL_CLASS = create_literal("ATE", arity=2, sep=" | ", name_tex="\\text{ATE}", sep_tex=" \\mid ")

    def __init__(self, outcome, treatment_condition, control_condition=None):
        super().__init__()
        self.name = "average treatment effect"

        if not isinstance(outcome, Variable):
            raise TypeError(f"outcome must be a Variable, not {type(outcome)}")

        if isinstance(treatment_condition, Variable):
            if control_condition:
                raise ValueError("if treatment_condition is a Variable, control_condition must be None")
            if treatment_condition.domain and not isinstance(treatment_condition.domain, BinaryDomain):
                raise ValueError("if treatment_condition is a Variable, it must be binary")
            control_condition = [treatment_condition.val == 0]
            treatment_condition = [treatment_condition.val == 1]

        self.outcome = outcome
        self.control_condition = self._validate_condition(control_condition, "control_condition")
        self.treatment_condition = self._validate_condition(treatment_condition, "treatment_condition")
        assert True

    def _validate_condition(self, condition, name):
        if isinstance(condition, dict):
            new_condition = []
            for k, v in condition.items():
                if isinstance(k, str):
                    k = Variable(k)
                if not isinstance(k, Variable):
                    raise TypeError(f"if dict is passed, {name} keys must be Variable or str, not {type(k)}")
                
                if isinstance(v, Variable):
                    raise TypeError(f"if dict is passed, {name} values must not be Variables")
                new_condition.append(EqualityEvent(k, v))
            return new_condition
        elif isinstance(condition, EqualityEvent):
            condition = [condition]
        
        if not isinstance(condition, list):
            try:
                condition = list(condition)
            except TypeError:
                raise TypeError(f"{name} must be dict or iterable, not {type(condition)}")
        for v in condition:
            if not isinstance(v, StatisticalEvent):
                raise TypeError(f"if a non-dict iterable is passed, {name} must contain only StatisticalEvent, not {type(v)}")
        
        return condition
    
    def _treatment_vars(self):
        return list(set(v.get_var() for v in self.treatment_condition + self.control_condition))
    
    def __repr__(self):
        return f"ATE(outcome={repr(self.outcome)}, treatment={self._treatment_vars()})"
    
    def expression(self):
        return Expectation(self.outcome, P(self.outcome, given=[do(c) for c in self.treatment_condition])) -\
            Expectation(self.outcome, P(self.outcome, given=[do(c) for c in self.control_condition]))
    
    def literal(self):
        vset = VarSet(self._treatment_vars(), left="", right="")
        return self.__class__.LITERAL_CLASS(self.outcome, vset)

class CATE(ATE):
    """Causal estimand for the conditional average treatment effect

    To define the conditional average treatment effect, it's necessary to specify 
    what is meant by treatment and control in this context, and you need to specify the
    subpopulation in which to measure the effect. You can 
    do this by passing either a dict or a list of StatisticalEvent objects to 
    each of the treatment_condition and control_condition arguments. If a dict 
    is passed, the keys must be Variable or string, and the values must not 
    be Variable. If a list is passed, it must contain only instances of 
    StatisticalEvent.

    Example:
        >>> # treatment condition is x = 1, control condition is x = 0 in both of these
        >>  # in both, we are measuring the effect in the subpopulation where z = 1
        >>> CATE(outcome, treatment_condition={"x": 1}, control_condition={"x": 0}, subpopulation={"z": 1})
        >>> CATE(
        ...     outcome,
        ...     treatment_condition=[EqualityEvent("x", 1)],
        ...     control_condition=[EqualityEvent("x", 0)],
        ...     subpopulation=[EqualityEvent("z", 1)]
        ... )
        >>>
        >>> # treatment condition is x = 1 and y = "red", control condition is x = 0 and y = "blue"
        >>> # we are measuring the effect in the subpopulation where z = 1
        >>> CATE(
        ...     outcome,
        ...     treatment_condition={"x": 1, y: "red"},
        ...     control_condition={"x": 0, y: "blue"},
        ...     subpopulation={"z": 1}
        ... )
        
    
    Args:
        outcome (Variable): the outcome variable
        treatment_condition (dict or list): the treatment condition
        control_condition (dict or list): the control condition
        subpopulation (dict or list): the subpopulation in which to measure the effect
    """
    LITERAL_CLASS = create_literal("CATE", arity=3, sep=" | ", name_tex="\\text{CATE}", sep_tex=" \\mid ")
    def __init__(self, outcome, treatment_condition, control_condition, subpopulation):
        super().__init__(outcome, treatment_condition, control_condition)
        self.name = "conditional average treatment effect"
        self.subpopulation = self._validate_condition(subpopulation, "subpopulation")
    
    def _control_vars(self):
        return [v.get_var() for v in self.subpopulation]
    
    def __repr__(self):
        return f"<CATE treatment_vars={self._treatment_vars()}, outcome={self.outcome}, control_vars={self._control_vars()}>"

    def expression(self):
        tc = [do(c) for c in self.treatment_condition]
        oc = [do(c) for c in self.control_condition]
        return Expectation(self.outcome, P(self.outcome, given=tc + self.subpopulation)) -\
            Expectation(self.outcome, P(self.outcome, given=oc + self.subpopulation))
    
    def literal(self):
        intervention_set = VarSet(self._treatment_vars(), left="", right="")
        control_set = VarSet(self._control_vars(), left="", right="")
        return self.__class__.LITERAL_CLASS(self.outcome, intervention_set, control_set)
