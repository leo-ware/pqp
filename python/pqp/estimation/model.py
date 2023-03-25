import numpy as np
from pqp.symbols.variable import Variable
from pqp.parametric.distribution import Distribution
from pqp.causal.graph import Graph

class Model:
    def __init__(self, dist, graph):
        """
        The model class is a wrapper around a distribution and a graph. It contains a combination
        of the causal and parametric assumptions.

        Args:
            dist (Distribution): The distribution to use for estimation
            graph (Graph): The graph to use for identification
        """
        if not isinstance(dist, Distribution):
            raise TypeError("dist must be a Distribution")
        if not isinstance(graph, Graph):
            raise TypeError("graph must be a Graph")

        self.dist = dist
        self.graph = graph
    
    def estimand(self, v, do=None, given=None):
        """Identifies an interventional distribution"""
        if do == None:
            do = []
        if given == None:
            given = []
        return self.graph.idc(y=[Variable(v)], x=[Variable(i) for i in do], z=[Variable(i) for i in given])
    
    # def expectation(self, var, do=None, given=None):
    #     """Calculates an expectated value of a variable after intervention and conditioning to specific values
        
    #     You might use this to calculate the average treatment effect by finding the expected
    #     outcome after treatment and subtracting the expected outcome after control.

    #     Args:
    #         var (str): The variable to calculate the expectation of
    #         do (dict): A dictionary of variables (str) to intervene on
    #         given (dict): A dictionary of variables (str) to condition on
        
    #     Returns:
    #         The expected value of the variable, a number
    #     """
        
    def ate(self, outcome, do_control, do_treat):
        """Convenience function for calculating the average treatment effect

        As a reminder, the average treatment effect is defined as,

        $$
        ATE = E[Y | do(Treatment) = 1] - E[Y | do(Treatment) = 0]
        $$

        You can choose how treatment and control are defined using the do_control and do_treat
        dictionaries. This means you can do multivariate interventions.
        
        Args:
            var (str): The outcome variable
            do_control (dict): A dictionary of variables (str) to intervene on for the control group
            do_treat (dict): A dictionary of variables (str) to intervene on for the treatment group
        
        Returns:
            The average treatment effect, a number
        """
        return self.expectation(outcome, do=do_treat) - self.expectation(outcome, do=do_control)

    def cate(self, outcome, do_control, do_treat, given):
        """Convenience function for calculating the conditional average treatment effect

        As a reminder, the conditional average treatment effect is defined as,

        $$
        CATE = E[Y | do(Treatment) = 1, Z=z] - E[Y | do(Treatment) = 0, Z=z]
        $$

        You can choose how treatment and control are defined using the do_control and do_treat
        dictionaries. This means you can do multivariate interventions and conditions.

        Args:
            var (str): The outcome variable
            do_control (dict): A dictionary of variables (str) to intervene on for the control group
            do_treat (dict): A dictionary of variables (str) to intervene on for the treatment group
            given (dict): A dictionary of variables (str) to condition on
        Returns:
            The conditional average treatment effect, a number
        """
        return self.expectation(outcome, do=do_treat, given=given) -\
            self.expectation(outcome, do=do_control, given=given)