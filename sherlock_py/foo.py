

import pprint
import json

try:
    del sys.modules["backend"]
except:
    pass

import backend

d = [
    ("A", "B"),
    ("B", "C"),
]

c = [
    ("A", "C"),
]

res = backend.id(d, c, ["C"], ["A"], [])
print()
print(res)
print()
pprint.pprint(json.loads(res))
