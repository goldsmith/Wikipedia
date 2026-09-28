from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import wikipedia

project = 'wikipedia'
copyright = '2013–2026, Jonathan Goldsmith and contributors'
release = '.'.join(map(str, wikipedia.__version__))
version = release
extensions = ['sphinx.ext.autodoc']
master_doc = 'index'
html_theme = 'alabaster'
exclude_patterns = []
