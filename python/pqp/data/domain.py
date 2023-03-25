from pqp.utils.exceptions import DomainValidationError

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class Domain(ABC):
    @abstractmethod
    def get_cardinality(self):
        """The number of possible values a variable can take on"""
        raise NotImplementedError
    
    @abstractmethod
    def __contains__(self, value):
        """Returns whether a value is in the domain"""
        raise NotImplementedError
    
    def validate(self, values):
        """Validates that a list of values is in the domain

        Args:
            values (list): a list of values to validate

        Returns:
            bool: True if all values are in the domain, False otherwise
        """
        return all([value in self for value in values])
    
    def validate_or_throw(self, values):
        """Validates that a list of values is in the domain, throws an error if not

        Args:
            values (list): a list of values to validate

        Raises:
            ValueError: if any value is not in the domain
        """
        for val in values:
            if not val in self:
                raise DomainValidationError(f"Value {val} is not in domain {self}")

class DiscreteDomain(Domain, ABC):
    @abstractmethod
    def get_values(self):
        """Returns a list of all possible values in the domain"""
        raise NotImplementedError

class IntegerDomain(DiscreteDomain):
    def __init__(self, values):
        """Represents a domain for which a variable is an integer in a range

        Args:
            values (list): a list of integers, max and min of which are bounds of the range
        """
        try:
            values = list(values)
        except TypeError:
            raise ValueError("values must be an iterable")
        
        self.min = np.min(values)
        self.max = np.max(values)
    
    def get_values(self):
        return list(range(self.min, self.max + 1))
    
    def check_int(self, val):
        return int(val) == val
    
    def get_cardinality(self):
        return self.max - self.min + 1
    
    def __repr__(self):
        return f"IntegerDomain([{self.min}, {self.max}])"
    
    def __contains__(self, value):
        return self.check_int(value) and self.min <= value <= self.max

class CategoricalDomain(DiscreteDomain):
    def __init__(self, values):
        """Represents a categorical domain for a variable, specified by a list of values

        Args:
            values (list): a list, unique elements of which are possible values for the variable
        """
        try:
            values = list(values)
        except TypeError:
            raise ValueError("Discrete domains must specify values")
        self.values = set(values)
    
    def get_values(self):
        return list(self.values)
    
    def get_cardinality(self):
        return len(self.values)
    
    def __contains__(self, value):
        return value in self.values
    
    def __repr__(self):
        if len(repr(self.values)) > 10:
            return f"CategoricalDomain(cardinality={self.get_cardinality()})"
        else:
            return f"CategoricalDomain({repr(self.values)})"

class BinaryDomain(CategoricalDomain):
    def __init__(self):
        super().__init__([0, 1])
    
    def __repr__(self):
        return "BinaryDomain()"

class ContinuousDomain(Domain):
    def get_cardinality(self):
        return float("inf")

class RealDomain(ContinuousDomain):
    """Represents a continuous domain for a variable, delimited by min and max values

    Args:
        values (list): the min and max of this list are taken as the min and max of the domain
    """
    def __init__(self, values):
        try:
            values = list(values)
        except TypeError:
            raise ValueError("Continuous domains must specify values")
        self.min = np.min(values)
        self.max = np.max(values)
    
    def __repr__(self):
        return f"RealDomain([{self.min}, {self.max}])"
    
    def __contains__(self, value):
        return self.min <= value <= self.max

def _infer_domain_type_values(values):
    precendence = {
        'binary': 4,
        'integer': 3,
        'continuous': 2,
        'discrete': 1,
    }

    use = 'binary'
    for val in values:
        if (type(val) == bool or (type(val) == int and val in [0, 1])):
            pass
        elif ((type(val) == int) or (type(val) == float and int(val) == val)) and \
            (precendence[use] >= precendence['integer']):
            use = 'integer'
        elif (type(val) == float) and (precendence[use] >= precendence['continuous']):
            use = 'continuous'
        else:
            use = 'discrete'
            break
    return use

def _infer_domain_type_array(array):
    if isinstance(array, pd.Series):
        array = array.values
    
    if array.dtype == bool:
        return 'binary'
    elif array.dtype == int:
        if list(sorted(list(np.unique(array)))) == [0, 1]:
            return 'binary'
        return 'integer'
    elif array.dtype == float:
        return 'continuous'
    else:
        return 'discrete'

def infer_domain_type(vals):
    """Attempts to infer the best domain type to use of a list of values

    The rules for determining this are somewhat complicated. You should run this and
    inspect the result before use.

    Args:
        vals (iterable): a list of values to infer the domain type of
    """
    try:
        iter(vals)
    except TypeError:
        raise TypeError("vals must be iterable")

    if isinstance(vals, pd.Series) or isinstance(vals, np.ndarray):
        return _infer_domain_type_array(vals)
    else:
        return _infer_domain_type_values(vals)

def make_domain(domain_type, values=None):
    """Generates a domain object from a string and optional values

    Options:
        discrete: values must be specified
        continuous: min and max of `values` used to specify domain
        binary: values are ignored
        integer: min and max of `values` used to specify domain
        infer: attempt to guess
    
    Args:
        domain_type (str): one of 'discrete', 'continuous', 'integer', 'binary' or 'infer'
        values (list): the values of the domain

    """
    if domain_type == "discrete":
        return CategoricalDomain(values)
    elif domain_type == "continuous":
        return RealDomain(values)
    elif domain_type == "binary":
        return BinaryDomain()
    elif domain_type == "integer":
        return IntegerDomain(values)
    elif domain_type == "infer":
        return make_domain(infer_domain_type(values), values)
    else:
        raise ValueError(f"Invalid domain type {domain_type}, must be one of 'discrete', 'continuous', or 'binary'")
