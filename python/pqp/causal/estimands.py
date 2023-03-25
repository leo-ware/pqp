from pqp.symbols import *
from abc import ABC, abstractmethod

class CausalEstimand:
    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()
    
    @abstractmethod
    def expression(self):
        raise NotImplementedError()

class ATE(CausalEstimand):
    def __init__(self, outcome, treatment_condition, control_condition):
        if not isinstance(outcome, Variable):
            raise TypeError(f"outcome must be a Variable, not {type(outcome)}")

        self.outcome = outcome
        self.control_condition = self._validate_condition(control_condition, "control_condition")
        self.treatment_condition = self._validate_condition(treatment_condition, "treatment_condition")
    
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
            condition = new_condition
        else:
            if not isinstance(condition, list):
                try:
                    condition = list(condition)
                except TypeError:
                    raise TypeError(f"{name} must be dict or iterable, not {type(condition)}")
            for v in condition:
                if not isinstance(v, StatisticalEvent):
                    raise TypeError(f"if a non-dict iterable is passed, {name} must contain only StatisticalEvent, not {type(v)}")
        
        return condition
    
    def treatment_vars(self):
        return [v.get_var() for v in self.treatment_condition + self.control_condition]
    
    def __repr__(self):
        return f"<ATE treatment_vars={self.treatment_vars()}, outcome={self.outcome}>"
    
    def expression(self):
        return Expectation(self.outcome, P(self.outcome, given=[do(c) for c in self.treatment_condition])) -\
            Expectation(self.outcome, P(self.outcome, given=[do(c) for c in self.control_condition]))

class CATE(ATE):
    def __init__(self, outcome, treatment_condition, control_condition, subpopulation):
        super().__init__(outcome, treatment_condition, control_condition)
        self.subpopulation = self._validate_condition(subpopulation, "subpopulation")
    
    def control_vars(self):
        return [v.get_var() for v in self.subpopulation]
    
    def __repr__(self):
        return f"<CATE treatment_vars={self.treatment_vars()}, outcome={self.outcome}, control_vars={self.control_vars()}>"

    def expression(self):
        tc = [do(c) for c in self.treatment_condition]
        oc = [do(c) for c in self.control_condition]
        return Expectation(self.outcome, P(self.outcome, given=tc + self.subpopulation)) -\
            Expectation(self.outcome, P(self.outcome, given=oc + self.subpopulation))
