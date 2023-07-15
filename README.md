# PQP

The name `pqp` is short for *Pourquoi pas?*. This phrase is French for *why not?*, because "Why not?" was the question we asked ourselves when we found there was no maintained, open-source package for structural causal modeling in Python. The package provides a convenient interface for causal modeling along with routines for identification, estimation, and visualization.

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
causal_estimand = ATE(y, {x: 1}, {x: 0})
estimator = g.identify(causal_estimand)
print(estimator)

# >>> E_(y) [ Σ_(z) [ [P(x = 1, y, z) * P(z) / P(x = 1, z)] ] ] - E_(y) [ Σ_(z) [ [P(x = 0, y, z) * P(z) / P(x = 0, z)] ] ]

```

## Further Reading

For more information, see the documentation at [https://leo-ware.github.io/pqp/](https://leo-ware.github.io/pqp/).

The source code is available at [https://github.com/leo-ware/pqp](https://github.com/leo-ware/pqp).

## About

This package was created by Leo Ware as part of his undergraduate capstone project at Minerva University.