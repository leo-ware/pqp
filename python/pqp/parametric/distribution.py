from abc import ABC, abstractmethod
from pqp.symbols import *


class Distribution(ABC):
    @abstractmethod
    def __init__(self, data, observed=None, *args, **kwargs):
        """Initialize a distribution
        Args:
            data (Data): The data to use for the distribution
            observed (list): The variables which are considered observed, defaults to all
        """
        pass

    def approx(self, expr, assignments=None):
        """Approximated the value of an expression

        Args:
            estimand (AbstractExpression): The expression to approximate
            assignments (dict): dict of variable assignments (optional)
        
        Returns:
            float: the approximate value of the expression
        """
        if not isinstance(expr, AbstractExpression):
            raise TypeError("expr must be an AbstractExpression object")
        
        if assignments is not None:
            expr = expr.assign(assignments)

        if isinstance(expr, P):
            res = self.approx_p(expr)
        elif isinstance(expr, Marginal):
            res = self.approx_marginal(expr)
        elif isinstance(expr, Product):
            res = self.approx_product(expr)
        elif isinstance(expr, Quotient):
            res = self.approx_quotient(expr)
        elif isinstance(expr, Difference):
            res = self.approx_difference(expr)
        elif isinstance(expr, Expectation):
            res = self.approx_expectation(expr)
        else:
            raise ValueError("Unsupported expression type: {}".format(type(expr)))
        
        return res
    
    @abstractmethod
    def approx_p(self, expr):
        pass

    @abstractmethod
    def approx_marginal(self, expr):
        pass

    @abstractmethod
    def approx_product(self, expr):
        pass

    @abstractmethod
    def approx_quotient(self, expr):
        pass

    @abstractmethod
    def approx_difference(self, expr):
        pass

    @abstractmethod
    def approx_expectation(self, expr):
        pass
