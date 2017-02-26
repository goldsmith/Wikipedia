# -*- coding: utf-8 -*-
import codecs
import os
import re
import setuptools
from mediawikiapi import __version__

def local_file(file):
  return codecs.open(
    os.path.join(os.path.dirname(__file__), file), 'r', 'utf-8'
  )

install_reqs = [
  line.strip()
  for line in local_file('requirements.txt').readlines()
  if line.strip() != ''
]

setuptools.setup(
  name = "mediawikiapi",
  version = __version__,
  author = "Taras Lehinevych",
  author_email = "mediawikiapi@taraslehinevych.me",
  description = "Wikipedia API for Python",
  license = "MIT",
  keywords = "python wikipedia API mediawiki",
  url = "https://github.com/lehinevych/MediaWikiAPI",
  install_requires = install_reqs,
  packages = ['mediawikiapi'],
  long_description = local_file('README.rst').read(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ]
)
