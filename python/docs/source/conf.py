# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import toml
import datetime
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# DO NOT EDIT!!! This information is automatically generated from pyproject.toml

with open("../../../pyproject.toml") as f:
    pyproject = toml.load(f)["project"]

project = pyproject["name"]
author = pyproject["authors"][0]["name"]
release = pyproject["version"]
copyright = f'{datetime.datetime.now().year}, {author}'

print(project, author, release, copyright)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.githubpages',
    'sphinx_automodapi.automodapi'
]

templates_path = ['_templates']
exclude_patterns = []
numpydoc_show_class_members = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# html_sidebars = {
#     "**": ["sbt-sidebar-nav.html"]
# }

html_favicon = 'favicon.ico'