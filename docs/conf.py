import os
import sys
sys.path.insert(0, os.path.abspath(".."))

project = 'Thermodynamics'
author = 'Mark Hoehne'
release = '0.2.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
