import os
import json

# params
name = "PQP"
notebooks = [
    "writeup.ipynb",
    "agg.ipynb"
]

# code
name = f"{name}.ipynb"
os.chdir("/Users/leoware/Documents/pqp/writeup")
os.system(f"touch {name}")

init_content = """{
 "cells": [
  {
   "attachments": {},
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "foo"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  },
  "orig_nbformat": 4
 },
 "nbformat": 4,
 "nbformat_minor": 2
}"""

with open(name, "w") as f:
    f.write(init_content)

with open(name, "r") as f:
    notebook = json.load(f)

cells = []
for notebook in notebooks:
    with open(notebook, "r") as f:
        notebook = json.load(f)
    cells.extend(notebook["cells"])
notebook["cells"] = cells

with open(name, "w") as f:
    json.dump(notebook, f)

# os.system(f'jupyter nbconvert --to pdf --out out/final.pdf "{name}"')