from abc import ABC, abstractmethod
from pqp.symbols import *
from pqp.refutation import entrypoint, Result, Step
from pqp.identification.estimands import AbstractCausalEstimand


class EstimationResult(Result):
    """Stores the result of estimation

    Attributes:
        value (float): the estimated value
    """
    _keys = ["value"]
    def __repr__(self):
        # for dep in self.get_nested_dependencies():
        #     if isinstance(dep, AbstractCausalEstimand):
        #         return f"EstimationResult(value={self.value}, estimand={dep})"
        return f"EstimationResult(value={self.value})"


class Estimator(Result, ABC):
    """Abstract base class for estimators"""
    def __init__(self, op):
        step = Step(f"Fit {self.__class__.__name__}")
        super().__init__(op, step)

    @abstractmethod
    def estimate(self, expr: AbstractExpression, assignments=None):
        """Estimate the value of an expression

        Args:
            expr (AbstractExpression): The expression to estimate
            assignments (dict): dict of variable assignments (optional)
        
        Returns:
            EstimationResult: the result of the estimation
        """
        pass
    
    @abstractmethod
    def get_observed(self):
        """Return the set of Variables that are considered observed in the model
        
        Returns:
            set: the set of observed variables
        """
        pass

    @abstractmethod
    def domain_of(self, var):
        """Return the domain of a variable
        
        Args:
            var (Variable or str): The variable to get the domain of
        
        Returns:
            Domain: the domain of the variable
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(observed=[{', '.join(map(str, self.get_observed()))}])"

    def approx(self, expr, assignments=None):
        """Approximated the value of an expression

        Args:
            expr (AbstractExpression): The expression to approximate
            assignments (dict): dict of variable assignments (optional)
        
        Returns:
            float: the approximate value of the expression
        """
        if not isinstance(expr, AbstractExpression) and not (isinstance(expr, Result) and hasattr(expr, "statistical_estimand")):
            raise TypeError("expr must be an AbstractExpression object or Result")
        
        if isinstance(expr, Result):
            id_result = expr
            expr = expr.statistical_estimand
        else:
            id_result = None
        
        if assignments is not None:
            expr = expr.assign(assignments)
        
        free = expr.free_variables()
        observed = self.get_observed()
        if not free.issubset(observed):
            raise ValueError("cannot estimand an equation with variables not in" +
                f" observed {free - obeserved}")
        
        est = self._approx(expr)
        return est

    def _approx(self, expr):
        if isinstance(expr, P):
            res = self._approx_p(expr)
        elif isinstance(expr, Marginal):
            res = self._approx_marginal(expr)
        elif isinstance(expr, Product):
            res = self._approx_product(expr)
        elif isinstance(expr, Quotient):
            res = self._approx_quotient(expr)
        elif isinstance(expr, Difference):
            res = self._approx_difference(expr)
        elif isinstance(expr, Expectation):
            res = self._approx_expectation(expr)
        else:
            raise ValueError("Unsupported expression type: {}".format(type(expr)))
        return res
    
    @abstractmethod
    def _approx_p(self, expr):
        pass

    @abstractmethod
    def _approx_marginal(self, expr):
        pass

    @abstractmethod
    def _approx_product(self, expr):
        pass

    @abstractmethod
    def _approx_quotient(self, expr):
        pass

    @abstractmethod
    def _approx_difference(self, expr):
        pass

    @abstractmethod
    def _approx_expectation(self, expr):
        pass
