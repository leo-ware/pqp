
class PQPException(Exception):
    """Base class for exceptions in this module."""
    pass

class InferredDomainWarning(PQPException):
    """Warning raised when the domain of a variable is inferred from provided examples"""
    pass

class UnitDomainWarning(PQPException):
    """Warning raised when the domain of a variable has cardinality <= 1"""
    pass

class PositivityException(PQPException):
    """Exception raised when a nonpositive distribution is used"""
    pass

class DomainValidationError(PQPException):
    """Exception raised when domain is used with invalid values"""
    pass

class NumericalError(PQPException):
    """Exception raised when numerical methods fail"""
    pass

class CyclicGraphError(PQPException):
    """Exception raised when a graph is cyclic"""
    pass

# class HedgeError(Exception):
#     """Indicates that identification has failed"""
#     pass