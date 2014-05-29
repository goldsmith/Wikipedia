# -*- coding: utf-8 -*-
import os
import codecs

from setuptools import setup

long_description = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r', 'utf-8').read()

install_reqs = [
  line.strip()
  for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).readlines()
  if line.strip() != ''
]

setup(
  name = "wikipedia",
  version = "1.3dev",
  author = "Jonathan Goldsmith",
  author_email = "jhghank@gmail.com",
  description = "Wikipedia API for Python",
  license = "MIT",
  keywords = "python wikipedia API",
  url = "https://github.com/goldsmith/Wikipedia",
  install_requires = install_reqs,
  packages = ['wikipedia'],
  long_description = long_description,
  classifiers = [
    'Development Status :: 4 - Beta',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ],
)
