from pqp.symbols.variable import Variable
from pqp.symbols.relation import *
from pqp.symbols.p import P

def parse_json(exp):
    """Parses JSON returned from backend.id() into an Expression object.

    Args:
        exp (str or dict): The JSON string or parsed JSON object.
    
    Returns:
        Expression: The parsed expression.
    """
    if isinstance(exp, str):
        return parse_json(json.loads(exp))

    if exp["type"] == "Quotient":
        return Quotient(
            parse_json(exp["numer"]),
            parse_json(exp["denom"]),
        )
    elif exp["type"] == "Product":
        return Product(
            [parse_json(e) for e in exp["exprs"]],
        )
    elif exp["type"] == "Marginal":
        return Marginal(
            [Variable(x) for x in exp["sub"]],
            parse_json(exp["exp"]),
        )
    elif exp["type"] == "Hedge":
        return Hedge()
    elif exp["type"] == "P":
        return P(
            [Variable(e) for e in exp["vars"]],
            [Variable(e) for e in exp["given"]],
        )
    else:
        raise ValueError("Unknown expression type: " + exp["type"])
