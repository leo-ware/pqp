from pqp import *#Data, Graph, MultinomialEstimator, make_vars, do, ATE
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

n = 1000
np.random.seed(0)

effect_zx = 0.5
effect_xm = 0.5
effect_zy = 0.5
effect_my = 0.5

df = pd.DataFrame()
df["z"] = (np.random.uniform(0, 1, n) > 0.5).astype(int)
df["x"] = (np.random.uniform(0, 1, n) + df["z"] * effect_zx > 0.5).astype(int)
df["m"] = (np.random.uniform(0, 1, n) + df["x"] * effect_xm > 0.5).astype(int)
df["y"] = (np.random.uniform(0, 1, n) + effect_my * df["m"] + effect_zy * df["z"] > 0.5).astype(int)

df.describe()

