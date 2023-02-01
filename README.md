# PQP

The name `pqp` is short for *Pourquoi pas?*. This phrase is French for *why not?*, because "Why not?" was the question we asked ourselves when we found there was no maintained, open-source package for causal identification in Python. With this package, we provide a correct, performant, and intuitive implementation of Shpitser's ID algorithm for causal graphs, and we hope soon to provide more useful functionality to support causal inference in the structural causal modeling framework.

## Installation

The package can be installed from PyPi using `pip`:

```bash
pip install pqp
```

## Basic Usage

```python

from pqp.graph import Graph
from pqp.variable import make_vars

# create variables
x, y, z = make_vars("xyz")

# the backdoor model
g = Graph([
    x <= z,
    y <= z,
    y <= x,
])

# identification
estimand = g.idc([y], [x])
print(estimand)

# >>> Σ_(z) [ [P(z) * P(z, x, y) / P(z, x)] ]

```

## Further Reading

For more information, see the documentation at [https://leo-ware.github.io/pqp/](https://leo-ware.github.io/pqp/).

The source code is available at [https://github.com/leo-ware/pqp](https://github.com/leo-ware/pqp).

## About

This package was created by Leo Ware as part of his undergraduate capstone project at Minerva University.