# -*- coding: utf-8 -*-
import codecs
import os
import re
import setuptools


def local_file(file):
  return codecs.open(
    os.path.join(os.path.dirname(__file__), file), 'r', 'utf-8'
  )

install_reqs = [
  line.strip()
  for line in local_file('requirements.txt').readlines()
  if line.strip() != ''
]

version = re.search(
  "^__version__ = \((\d+), (\d+), (\d+)\)$",
  local_file('wikipedia/__init__.py').read(),
  re.MULTILINE
).groups()


setuptools.setup(
  name = "wikipedia_sections",
  version = '.'.join(version),
  author = "Sacha Vakili",
  author_email = "vakili.sacha@gmail.com",
  description = "Wikipedia API for Python extracting sections",
  license = "MIT",
  keywords = "python wikipedia API",
  url = "https://github.com/sachavakili/Wikipedia",
  install_requires = install_reqs,
  packages = ['wikipedia'],
  long_description = local_file('README.rst').read(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ],
  download_url='https://github.com/sachavakili/Wikipedia/archive/v2.0.tar.gz',
)
