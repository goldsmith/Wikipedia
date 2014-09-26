# -*- coding: utf-8 -*-
import codecs
import os
import re
import setuptools
try:
    from setuptools.command.test import test as TestCommand
except ImportError:
    pass


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def local_file(file):
  return codecs.open(
    os.path.join(os.path.dirname(__file__), file), 'r', 'utf-8'
  )


install_reqs = [
  line.strip()
  for line in local_file('requirements.txt').readlines()
  if line.strip() != ''
]
test_reqs = [
  line.strip()
  for line in local_file('test-requirements.txt').readlines()
  if line.strip() != ''
]

version = re.search(
  "^__version__ = \((\d+), (\d+), (\d+)\)$",
  local_file('wikipedia/__init__.py').read(),
  re.MULTILINE
).groups()


setuptools.setup(
  name = "wikipedia",
  version = '.'.join(version),
  author = "Jonathan Goldsmith",
  author_email = "jhghank@gmail.com",
  description = "Wikipedia API for Python",
  license = "MIT",
  keywords = "python wikipedia API",
  url = "https://github.com/goldsmith/Wikipedia",
  install_requires = install_reqs,
  test_requires = test_reqs,
  packages = ['wikipedia'],
  long_description = local_file('README.rst').read(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ],
  cmdclass = {'test': Tox},
  # Magic !
  zip_safe = False
)
