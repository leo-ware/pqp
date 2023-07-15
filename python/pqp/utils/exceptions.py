
class InferredDomainWarning(Warning):
    """Warning raised when the domain of a variable is inferred from provided examples"""
    pass

class UnitDomainWarning(Warning):
    """Warning raised when the domain of a variable has cardinality <= 1"""
    pass

class PositivityException(Exception):
    """Exception raised when a nonpositive distribution is used"""
    pass

class DomainValidationError(Exception):
    """Exception raised when domain is used with invalid values"""
    pass

class NumericalError(Exception):
    """Exception raised when numerical methods fail"""
    pass

# class HedgeError(Exception):
#     """Indicates that identification has failed"""
#     pass