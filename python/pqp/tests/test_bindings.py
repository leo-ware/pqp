from pqp_backend import id

def test_id():
    foo = id(
        [("x", "y")],
        [("x", "y")],
        ["x"],
        ["y"],
        []
    )
    assert foo == {"type": "Hedge"}