import numpy as np

from pqp.symbols import *
from pqp.data.domain import DiscreteDomain
from pqp.utils import attrdict
from pqp.utils.exceptions import NumericalError, PositivityException
from pqp.estimation.estimator import Estimator, EstimationResult
from pqp.data.data import Data
from pqp.refutation import entrypoint, Result, Operation

def _extract_assignments_expr(expr):
    context = {}
    for g in expr.vars + expr.given:
        if isinstance(g, EqualityEvent):
            context[g.var.name] = g.val
        elif isinstance(g, Variable):
            raise ValueError("MultinomialEstimator cannot evaluate expression "
            f"containing the free variable {repr(g)}")
        elif isinstance(g, InterventionEvent):
            raise ValueError(f"MultinomialEstimator cannot approximate the do-expression {repr(g)},"
                " you must first identify the expression")
        elif isinstance(g, Event):
            raise NotImplementedError(f"MultinomialEstimator cannot evaluate Event of type {type(g)}")
        else:
            raise TypeError(f"Values behind the conditioning bar must be Variable or Event, not {type(g)}")
    
    expr = P(
        [x if isinstance(x, Variable) else x.get_var() for x in expr.vars],
        [x if isinstance(x, Variable) else x.get_var() for x in expr.given]
        )
    
    return expr, context

class MultinomialEstimator(Estimator):  
    """Estimates the distribution of a categorical variable using a multinomial likelihood and dirichlet prior

    At a basic level, this estimator estimates the probability of an observation using the 
    proportion of past observations which are identical. When prior is set to zero, this is
    exactly what it does, and positivty is not guaranteed.

    If you set prior to a positive value, this is interpreted as a number of "virtual"
    observations. The estimator behaves as if, before fitting to the data, it had already 
    seen this many data points. It distributes this likelihood evenly across all possible
    observations in the domain of the variables. This guarantess positivity.

    Args:
        data (Data): The data to use for the distribution
        observed (list): The variables which are considered observed, defaults to all
        prior (float): The prior strength, defaults to 0
        coerce (bool): If True, coerce the data to a Data object, defaults to True
    """  
    def __init__(self, data, observed=None, prior=0, coerce=True):
        if not isinstance(data, Data):
            if coerce:
                data = Data(data)
            else:
                raise TypeError(f"data must be a Data object if coerce is False, not {type(data)}")
        
        op = Operation(MultinomialEstimator, [], {"data": data, "observed": observed, "prior": prior, "coerce": coerce})
        super().__init__(op)
        
        for name, var in data.vars.items():
            if var.domain is None:
                raise ValueError(f"{var} has no domain")
            if not isinstance(var.domain, DiscreteDomain):
                if coerce:
                    self.step.write(f"Coercing {var} to discrete")
                    data.quantize(var)
                else:
                    raise ValueError(f"{var} has domain {domain} which is not discrete,"
                        " pass a discrete domain or set coerce=True to quantize the data")
        
        self.data = data
        self.observed_names = set(v.name if isinstance(v, Variable) else v for v in \
            (observed or data.vars.keys()))

        if not self.observed_names.issubset(data.vars.keys()):
            raise ValueError(f"observed variables must be a subset of the variablesin Data")

        # number of prior "observations" at each point in the observed domain
        self.prior = prior / self._domain_size(self.observed_names)
        # combined count of actual observations and virtual, prior "observations"
        self.prior_posterior_obs = prior + self.data.n

        self.step.assume("Multinomial likelihood")
        self.step.assume("Dirichlet prior")
    
    def get_observed(self):
        return set(self.data.vars[v] for v in self.observed_names)
    
    def domain_of(self, var):
        if isinstance(var, Variable):
            var = var.name
        try:
            return self.data.vars[var].domain
        except KeyError:
            raise ValueError(f"{var} is not in the data")
    
    def _domain_size(self, var_names):
        return np.prod([self.domain_of(col).get_cardinality() for col in var_names])

    def _df_where_conditions(self, assignments):
        df = self.data.df
        for var, val in assignments.items():
            if isinstance(var, Variable):
                var = var.name
            df = df[df[var] == val]
            df = df.drop(var, axis=1)
        return df
    
    def _count_where_conditions(self, assignments, df):
        mask = np.ones(df.shape[0], dtype=bool)
        for var, val in assignments.items():
            if isinstance(var, Variable):
                var = var.name
            mod = df[var] == val
            mask = mask & mod
        return mask.sum()
    
    def _approx_p(self, expr: P):
        expr, context = _extract_assignments_expr(expr)
        
        # perform conditioning
        data = self._df_where_conditions({v.name: context[v.name] for v in expr.given})
        if data.shape[0] == self.prior == 0:
            raise PositivityException(f"MultinomialEstimator cannot estimate {expr} because prior is "
                "zero and there are no observations consistent with the conditioning")
        denom = data.shape[0]

        # find subset where expression is true
        n_instances = self._count_where_conditions({v.name: context[v.name] for v in expr.vars}, data)
        
        # calculate prior stuff
        domain_after_conditioning = self._domain_size(self.observed_names - set(var.name for var in expr.given))
        domain_after_condition_assign = self._domain_size(self.observed_names - set(var.name for var in expr.given + expr.vars))
        virtual_denom = domain_after_conditioning*self.prior
        virtual_instances = domain_after_condition_assign*self.prior

        # add prior stuff in
        n_total_instances = n_instances + virtual_instances
        total_denom = denom + virtual_denom
        return n_total_instances / total_denom
    
    def _approx_marginal(self, expr: Marginal):
        acc = 0
        if expr.sub:
            summation_var = expr.sub[0]
            assert isinstance(summation_var, Variable)
            expr = expr.expr if len(expr.sub) == 1 else Marginal(expr.sub[1:], expr.expr)
            try:
                for val in self.domain_of(summation_var).get_values():
                    acc += self._approx(expr.assign(summation_var, val))
            except KeyError:
                raise ValueError(f"summation variable '{summation_var}' not found")
        return acc
    
    def _approx_product(self, expr: Product):
        acc = 1
        for e in expr.expr:
            acc *= self._approx(e)
        return acc
    
    def _approx_quotient(self, expr: Quotient):
        numer = self._approx(expr.numer)
        denom = self._approx(expr.denom)
        if denom == 0:
            raise PositivityException(f"Division by zero in {expr}, consider seeting prior to a nonzero value"
                "when initializing the estimator")
        return numer/denom
    
    def _approx_difference(self, expr: Difference):
        return self._approx(expr.a) - self._approx(expr.b)
    
    def _approx_expectation(self, expr: Expectation):
        summation_var = expr.sub
        acc = 0
        prob_acc = 0
        for val in self.domain_of(summation_var).get_values():
            prob = self._approx(expr.expr.assign(summation_var, val))
            prob_acc += prob
            acc += prob * val
            # foo
        
        if abs(prob_acc - 1) > 0.1:
            raise NumericalError(f"Probabilities do not sum to 1 (prob_acc = {prob_acc})")

        return acc
    
    @entrypoint("Estimation", result_class=EstimationResult)
    def estimate(self, estimand, assignments=None, step=None):
        if assignments is None:
            assignments = {}
        if step is None:
            raise ValueError("step must be provided")

        flag = False
        if isinstance(estimand, Result):
            try:
                estimand = estimand.identified_estimand
            except AttributeError:
                flag = True
        if flag or not isinstance(estimand, AbstractExpression):
            raise ValueError("estimand must be Result from identification or expression")

        step.write("Performing brute force estimation using a multinomial likelihood " +
            "and dirichlet prior.")
        approx = self.approx(estimand, assignments=assignments)
        step.result("value", approx)
