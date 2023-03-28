
# human interpretability
class Step:
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
        self._assumptions.append(assumption)
        self._log.append(assumption)
    
    def result(self, key, value):
        self._results[key] = value

# computer replicability
class Operation:
    def __init__(self, op, args, kwargs):
        self.op = op
        self.args = args
        self.kwargs = kwargs

class Result:
    def __init__(self, operation, step):
        self.operation = operation
        self.step = step

        for k, v in step._results.items():
            if k in ["operation", "step"]:
                raise ValueError("Cannot use reserved key: " + k)
            self.__setattr__(k, v)

def entrypoint(step_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            step = Step(step_name)
            op = Operation(func, args, kwargs)
            func_return = func(*args, **kwargs, step=step)
            assert func_return is None
            result = Result(op, step)
            return result
        return wrapper
    return decorator


# class CheckResult:
#     def __init__(self, success, name, desc=None, latex=None):
#         super().__init__(name, desc, latex)
#         self._success = None
    
#     @property
#     def success(self):
#         return self._success

# class Assumption(Reportable, ABC):
#     def __init__(self, name, desc=None, latex=None):
#         super().__init__(name, desc, latex)
#         self._checks = {}
#         self._check_results = dict.fromkeys(self.checks, None)
#         self._default_check = None
    
#     def _register_check(self, default):
#         """Method decorator for assumption checks
        
#         Checks must return a boolean or CheckResult. If you call
#         the decorator with default=True then the check will be
#         set as the default check for the assumption.
#         """
#         def transform_method(method, set_default=False):
#             self.checks[method.__name__] = method
#             if set_default is True:
#                 if self._default_check is None:
#                     self._default_check = method.__name__
#                 else:
#                     raise ValueError("Cannot set default check twice")
#             return method
        
#         if type(default) == bool:
#             return transform_method
#         else:
#             return transform_method(default)
    
#     @property
#     def checks(self):
#         return list(self._checks.keys())
    
#     def run_check(self, name=None):
#         if name is None:
#             if not self.checks:
#                 raise ValueError("No checks registered for assumption")

#             if self._default_check is None:
#                 name = self.checks[0]
#             else:
#                 name = self._default_check
        
#         try:
#             check = self._checks[name]
#         except KeyError:
#             raise ValueError(f"Check {name} not found, use one of {', '.join(self.checks)}")
        
#         result = check()
#         if type(result) == bool:
#             result = CheckResult(result, name)
        
#         if isinstance(result, CheckResult):
#             self._check_results[name] = result
#         else:
#             raise TypeError(f"Check must return a boolean or Check, not {type(result)}")
        
#         return result