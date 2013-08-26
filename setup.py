# -*- coding: utf-8 -*-
import os 

from setuptools import setup
from io import open

long_description = open(os.path.join(os.path.dirname(__file__), "README.rst"), encoding='utf-8').read().encode('ascii', 'ignore')

dependencies = [
    "beautifulsoup4",
    "requests==1.2.3"
    "wsgiref==0.1.2"
]

setup(
    name = "wikipedia",
    version = "0.9.8",
    author = "Jonathan Goldsmith",
    author_email = "jhghank@gmail.com",
    description = "Wikipedia API for Python",
    license = "MIT",
    keywords = "python wikipedia API",
    url = "https://github.com/goldsmith/Wikipedia",
    install_requires = dependencies,
    packages = ['wikipedia'],
    long_description = long_description,
    classifiers = (
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
    ),
)