from collections import deque
from pqp.utils import order_graph

class Assumption:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Assume: {self.name}"

class Derived:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"Derived: {self.name} = {self.value}"

# human interpretability
class Step:
    """Human-interpretable notes on how a result was derived"""
    def __init__(self, name):
        self._name = name
        self._log = [] # list of strings, substeps, assumption, expression
        self._assumptions = []
        self._results = {}
    
    def substep(self, name):
        s = Step(name)
        self._log.append(s)
        return s

    def write(self, msg):
        self._log.append(msg)
    
    def assume(self, assumption):
        if not isinstance(assumption, Assumption):
            assumption = Assumption(assumption)
        self._assumptions.append(assumption)
        self._log.append(assumption)
    
    def result(self, key, value):
        self._log.append(Derived(key, value))
        self._results[key] = value
    
    def _get_log_strings(self, pad=True):
        acc = []
        for l in self._log:
            if isinstance(l, Step):
                acc.append(l._name)
                acc.extend(["\t" + item if pad else item for item in l._get_log_strings(pad=pad)])
            else:
                acc.append(str(l))
        return acc
    
    def explain(self, pad=True):
        """Print an explanation of the derivation of the result"""
        return self._name + "\n\t" + "\n\t".join(self._get_log_strings(pad=pad))

# computer replicability
class Operation:
    """Class used to track the computational graph of function calls which led to a result

    Attributes:
        op (function): the function which was called
        args (list): the arguments passed to the function
        kwargs (dict): the keyword arguments passed to the function
    """
    def __init__(self, op, args, kwargs):
        self.op = op
        self.args = args
        self.kwargs = kwargs

class Result:
    """Class to store results of computation and store dependencies in a graph"""
    _keys = None

    def __init__(self, operation, step):
        self.operation = operation
        self.step = step

        for k, v in step._results.items():
            if k in ["operation", "step"]:
                raise ValueError("Cannot use reserved key: " + k)
            if (self.__class__._keys is not None):
                if k not in self.__class__._keys:
                    raise AttributeError("Cannot add attribute " + k)
            self.__setattr__(k, v)
    
    def __repr__(self):
        stuff = {}
        if self.__class__._keys is not None:
            for k in self.__class__._keys:
                stuff[k] = getattr(self, k)
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in stuff.items())})"

    def __hash__(self):
        return hash(str(self))
    
    def get_dependencies(self):
        dependencies = []
        for args in self.operation.args:
            if isinstance(args, Result):
                dependencies.append(args)
        for kwargs in self.operation.kwargs.values():
            if isinstance(kwargs, Result):
                dependencies.append(kwargs)
        return dependencies
    
    def get_nested_dependencies(self):
        d = deque([self])
        all_results = {}
        while d:
            r = d.popleft()
            deps = r.get_dependencies()
            all_results[r] = deps
            for dep in deps:
                if dep not in all_results:
                    d.append(dep)
        return order_graph(all_results)[::-1]

    def explain(self, nested=False):
        """Prints a human-readable explanation of the result to the console.
        
        Args:
            nested (bool): if True, will print the explanation of all prior steps as well
        """
        if nested:
            deps = self.get_nested_dependencies()
        else:
            deps = [self]
        
        for res in deps:
            print(res.step.explain())
    
    def explain_all(self):
        """Prints a human-readable explanation of the result to the console, including all prior steps.
        Equivalent to calling self.explain(nested=True)"""
        self.explain(nested=True)

def entrypoint(step_name, result_class=Result):
    """Wrapper for logical steps in the assumption management system

    Args:
        step_name (str): the name of the step (human readable)
        result_class (class): used to store results of the step, must be a subclass of `Result`
    Returns:
        decorator: wrapper for functions implementing logical steps in an analysis
    
    This function returns a a decorator which can be used to wrap a method implementing a step, a 
    `Step` instance is passed as a keyword argument ("step") to the method and should 
    be used to record substeps, assumptions, and results. The method should not return a value.

    The three core constructs of the assumption management system are `Assumption`a, `Step`s, and 
    `Result`s. A step is a logical unit of work encapsulated in a single method, which may be 
    composed of multiple substeps. During the process of calculation, the method can report 
    logical substeps, assumptions it is making, results as they are computed, and notes for 
    the user. This information is consolidated into the `Step` object, which stores references
    to previous steps in the analysis in a graph representing the entire computation. This way,
    metadata about the computation is available at all times and can be used by both the user and
    automated sensitivity analysis tools.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            step = Step(step_name)
            op = Operation(func, args, kwargs)
            func_return = func(*args, **kwargs, step=step)
            assert func_return is None, "entrypoint functions must not return a value"

            result = result_class(op, step)
            return result
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator
