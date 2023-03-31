Quickstart
================

Installation
------------
Install ``pqp`` using ``pip``

.. code-block:: bash

    pip install pqp

Usage
------

To characterize a causal effect, we need to specify three things:

#. **Causal Assumptions**: a graph representing the causal structural relationships between variables
#. **Parametric Assumptions**: a parametric model of the joint distribution of the data
#. **Causal Estimand**: an algebraic expression representing the causal effect of interest

Setup
++++++

To get started, we will spoof some data to run our analysis on.

.. code-block:: python

    import pandas as pd

    df = pd.DataFrame({
        "x": [0, 0, 0, 1, 1, 0],
        "z": [0, 1, 0, 1, 1, 0],
        "y": [0, 1, 0, 1, 1, 0],
    })

We can use the ``make_vars`` function to create a list of variables.

.. code-block:: python

    from pqp.symbols import make_vars
    x, y, z = make_vars("xyz")

Note that the names of these variables match the column names in the data frame.

Causal Assumptions
+++++++++++++++++++

We can then assemble these variables into a causal diagram using the ``Graph`` class. Here we will
build the famous front-door model.

Infix operators are used to construct causal relationships.  The ``<=`` operator is used to 
indicate causal influence from right to left, while the ``&`` operator is used to indicate
confounding.

.. code-block:: python

    from pqp.identification import Graph
    g = Graph([
        x & y,
        z <= x,
        y <= z,
    ])

We can use the ``.draw()`` method to visualize the causal diagram.

.. code-block:: python

    g.draw()

.. image:: imgs/frontdoor_viz.png
    :width: 400px


Parametric Assumptions
+++++++++++++++++++++++

For the purposes of this article, we will assume that the data is drawn from a multinomial
distribution. We can use the ``MultinomialEstimator`` class to specify the parametric assumptions.

.. code-block:: python

    from pqp.estimation import MultinomialEstimator
    estimator = MultinomialEstimator(df, prior=1)

The ``prior`` argument specifies the prior strength of the model.  The default is
zero, in which case the model fits through maximum likelihood. We are using a nonzero
value here because if you don't specify a prior, the model will not always give positive
probability estimates to events, which can cause problems when estimating causal effects.

If you don't specify a prior, don't worry though. If the estimator runs into a problem,
it will throw an exception and tell you what to do.

Causal Estimand
++++++++++++++++

For this example, we will estimate the average treatment effect of ``x`` on ``y``. First, 
we need to define the treatment and control conditions.

.. code-block:: python

    treatment_condition = [x.val == 1]
    control_condition = [x.val == 0]

Then, we can use the ``ATE`` class to define the causal estimand.

.. code-block:: python

    from pqp.estimation import ATE
    causal_estimand = ATE(y, treatment_condition, control_condition)
    
    #inspect the expression
    causal_estimand.expression().display()

.. image:: imgs/qs_causal_estimand.png
    :width: 500px

Identification and Estimation
+++++++++++++++++++++++++++++++

Now, we can first use the causal assumptions to identify the causal estimand, and then we can use the
parametric assumptions to estimate the causal effect.

To identify the causal relationships in the causal diagram, we can use the ``.identify()`` method.
For example, to identify the causal relationship between ``x`` and ``y``, we can use the following:

.. code-block:: python

    estimand = g.identify(causal_estimand).identified_estimand
    estimand.display()

.. image:: imgs/qs_stat_estimand.png
    :width: 600px

We can then use the ``.estimate()`` method to estimate the causal effect.

.. code-block:: python

    estimator.estimate(estimand)
    # => EstimationResult(value=0.4433808167141502)
