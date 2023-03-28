from abc import ABC, abstractmethod
from pqp.symbols import *
from pqp.refutation import entrypoint, Result, Step


class Estimator(Result, ABC):
    def __init__(self, op):
        step = Step(f"Fit {self.__class__.__name__}")
        super().__init__(op, step)

    @abstractmethod
    def estimate(self):
        pass

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
    def get_observed(self):
        pass
    
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
