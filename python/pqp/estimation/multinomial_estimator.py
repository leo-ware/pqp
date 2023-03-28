import numpy as np

from pqp.symbols import *
from pqp.data.domain import DiscreteDomain
from pqp.utils import attrdict
from pqp.utils.exceptions import NumericalError
from pqp.estimation.estimator import Estimator
from pqp.data.data import Data
from pqp.refutation import entrypoint, Result, Operation

def _new_multinomial(*args, **kwargs):
    return MultinomialEstimator(*args, **kwargs)

class MultinomialEstimator(Estimator):
    def __init__(self, data, observed=None, prior=0, coerce=True):
        """Initialize a categorical distribution

        This distribution models the data using a categorical likelihood function
        and a dirichlet prior. This distribution assumes that the data is discrete.

        Prior can be interpreted as a number of observations which have occured before any
        of the data was observed. These observations are distributed evenly (fractionally)
        over the domain of the variables. (Domain is inferred from presence in the dataset).
        This guarantees positivity, which is an important precondition for lots of the 
        subroutines in the package. If you run into mysterious divide by zero errors, consider
        giving this a positive value.

        Args:
            data (Data): The data to use for the distribution
            observed (list): The variables which are considered observed, defaults to all
            prior (float): The prior strength, defaults to 0
            coerce (bool): If True, coerce the data to a Data object, defaults to True
        """
        op = Operation(_new_multinomial, [], {"data": data, "observed": observed, "prior": prior, "coerce": coerce})
        super().__init__(op)

        if not isinstance(data, Data):
            if coerce:
                data = Data(data)
                self.operation.kwargs["data"] = data
            else:
                raise TypeError(f"data must be a Data object if coerce is False, not {type(data)}")
        
        for name, var in data.vars.items():
            if var.domain is None:
                raise ValueError(f"{var} has no domain")
            if not isinstance(var.domain, DiscreteDomain):
                if coerce:
                    data.quantize(var)
                else:
                    raise ValueError(f"{var} has domain {domain} which is not discrete,"
                        " pass a discrete domain or set coerce=True to quantize the data")
        
        self.data = data
        self.observed_names = set(observed or data.vars.keys())

        if not self.observed_names.issubset(data.vars.keys()):
            raise ValueError(f"observed variables must be a subset of the variablesin Data")

        # number of prior "observations" at each point in the observed domain
        self.prior = prior / self.domain_size(self.observed_names)
        # combined count of actual observations and virtual, prior "observations"
        self.prior_posterior_obs = prior + self.data.n
    
    def get_observed(self):
        return set(self.data.vars[v] for v in self.observed_names)
    
    def domain_size(self, var_names):
        return np.prod([self.domain_of(col).get_cardinality() for col in var_names])
    
    def domain_of(self, var):
        if isinstance(var, Variable):
            var = var.name
        try:
            return self.data.vars[var].domain
        except KeyError:
            raise ValueError(f"{var} is not in the data")
    
    def approx_p(self, expr: P):
        context = {}
        for g in expr.vars + expr.given:
            if isinstance(g, EqualityEvent):
                context[g.var.name] = g.val
            elif isinstance(g, Variable):
                ValueError("MultinomialEstimator cannot evaluate expression "
                f"containing the free variable {repr(g)}")
            elif isinstance(g, InterventionEvent):
                ValueError(f"MultinomialEstimator cannot approximate the do-expression {repr(g)},"
                    " you must first identify the expression")
            elif isinstance(g, Event):
                NotImplementedError(f"MultinomialEstimator"
             " cannot evaluate Event of type {type(g)}")
            else:
                raise TypeError(f"Values behind the conditioning bar must be Variable or Event, not {type(g)}")
        
        expr = P(
            [x if isinstance(x, Variable) else x.get_var() for x in expr.vars],
            [x if isinstance(x, Variable) else x.get_var() for x in expr.given]
            )

        data = self.data.df
        for cond in expr.given:
            if cond.name not in context:
                raise ValueError(f"Missing context for {cond.__repr__()}")
            data = data[data[cond.name] == context[cond.name]].drop(cond.name, axis=1)

        mask = np.ones(data.shape[0], dtype=bool)
        for var in expr.vars:
            if var.name not in context:
                raise ValueError(f"Missing context for {var.__repr__()}")
            mod = data[var.name] == context[var.name]
            mask = mask & mod
        
        # Consider the region consistent with conditioning
        #      1. the number of observations consistent with conditioning
        #      2. how many virtual observations the prior assigns to the region consistent with conditioning
        # sum these to get the total number of observations in the region consistent with conditioning
        nonconditioned_observed_domain = self.domain_size(self.observed_names - set(var.name for var in expr.given))
        virtual_obs = nonconditioned_observed_domain*self.prior
        virtual_nonvirtual_obs = virtual_obs + data.shape[0]

        # Do the same thing with the region consistent with conditioning and consistent with variable assignments
        matching_obs = mask.sum()
        matching_domain = self.domain_size(self.observed_names - set(var.name for var in expr.given + expr.vars))
        matching_virtual_obs = matching_domain*self.prior
        matching_virtual_nonvirtual_obs = matching_virtual_obs + matching_obs

        # return ratio between these two numbers
        return matching_virtual_nonvirtual_obs / virtual_nonvirtual_obs
    
    def approx_marginal(self, expr: Marginal):
        acc = 0
        if expr.sub:
            summation_var = expr.sub[0]
            expr = expr.expr if len(expr.sub) == 1 else Marginal(expr.sub[1:], expr.expr)
            try:
                for val in self.domain_of(summation_var).get_values():
                    acc += self._approx(expr.assign(summation_var, val))
            except KeyError:
                raise ValueError(f"summation variable '{summation_var}' not found")
        return acc
    
    def approx_product(self, expr: Product):
        acc = 1
        for e in expr.expr:
            acc *= self._approx(e)
        return acc
    
    def approx_quotient(self, expr: Quotient):
        return self._approx(expr.numer) / self._approx(expr.denom)
    
    def approx_difference(self, expr: Difference):
        return self._approx(expr.a) - self._approx(expr.b)
    
    def approx_expectation(self, expr: Expectation):
        summation_var = expr.sub
        acc = 0
        prob_acc = 0
        for val in self.domain_of(summation_var).get_values():
            prob = self._approx(expr.expr.assign(summation_var, val))
            prob_acc += prob
            acc += prob * val
        
        if abs(prob_acc - 1) > 0.1:
            raise NumericalError(f"Probabilities do not sum to 1 (prob_acc = {prob_acc})")

        return acc
    
    @entrypoint("Estimation")
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
        step.assume("Multinomial likelihood")
        step.assume("Dirichlet prior")
        approx = self.approx(estimand, assignments=assignments)
        step.result("value", approx)
