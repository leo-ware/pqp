from pqp.refutation.result import Result, Operation, Step, entrypoint


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
