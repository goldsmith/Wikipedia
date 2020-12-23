Wikipedia
=========

.. image:: https://travis-ci.org/goldsmith/Wikipedia.png?branch=master
  :target: https://travis-ci.org/goldsmith/Wikipedia
.. image:: https://pypip.in/d/wikipedia/badge.png
  :target: https://crate.io/packages/wikipedia
.. image:: https://pypip.in/v/wikipedia/badge.png
  :target: https://crate.io/packages/wikipedia
.. image:: https://pypip.in/license/wikipedia/badge.png
    :target: https://pypi.python.org/pypi/wikipedia/
    :alt: License

**Wikipedia** is a Python library that makes it easy to access and parse
data from Wikipedia.

Search Wikipedia, get article summaries, get data like links and images
from a page, and more. Wikipedia wraps the `MediaWiki
API <https://www.mediawiki.org/wiki/API>`__ so you can focus on using
Wikipedia data, not getting it.

.. code:: python

  >>> import wikipedia
  >>> print(wikipedia.summary("Wikipedia"))
  Wikipedia ( (listen) wik-ih-PEE-dee-ə or  (listen) wik-ee-) is a multilingual open-collaborative online encyclopedia created and maintained by a community of volunteer editors...

  >>> wikipedia.search("Barack")
  ['Barack Obama', 'Family of Barack Obama', 'Barack Obama Sr.', 'Barack (disambiguation)', 'Presidency of Barack Obama', 'Barack Adama', 'Barack (name)', 'Barack Obama religion conspiracy theories', 'Early life and career of Barack Obama', 'Michelle Obama']

  >>> ny = wikipedia.page("New York City")
  >>> ny.title
  'New York City'
  >>> ny.url
  'https://en.wikipedia.org/wiki/New_York_City'
  >>> ny.content
  'New York City (NYC), often called simply New York, is the most populous city in the United States.'...
  >>> ny.links[0]
  '10 Hudson Yards'

  >>> wikipedia.set_lang("fr")
  >>> wikipedia.summary("Python", sentences=1)
  'Python (prononcé en anglais /ˈpaɪ.θɑn/) est un langage de programmation interprété, multi-paradigme et multiplateformes.'

Note: this library was designed for ease of use and simplicity, not for advanced use. If you plan on doing serious scraping or automated requests, please use `Pywikipediabot <http://www.mediawiki.org/wiki/Manual:Pywikipediabot>`__ (or one of the other more advanced `Python MediaWiki API wrappers <http://en.wikipedia.org/wiki/Wikipedia:Creating_a_bot#Python>`__), which has a larger API, rate limiting, and other features so we can be considerate of the MediaWiki infrastructure.

Installation
------------

To install Wikipedia, simply run:

::

  $ pip install wikipedia

Wikipedia is compatible with Python 2.6+ (2.7+ to run unittest discover) and Python 3.3+.

Documentation
-------------

Read the docs at https://wikipedia.readthedocs.org/en/latest/.

-  `Quickstart <https://wikipedia.readthedocs.org/en/latest/quickstart.html>`__
-  `Full API <https://wikipedia.readthedocs.org/en/latest/code.html>`__

To run tests, clone the `repository on GitHub <https://github.com/goldsmith/Wikipedia>`__, then run:

::

  $ pip install -r requirements.txt
  $ bash runtests  # will run tests for python and python3
  $ python -m unittest discover tests/ '*test.py'  # manual style

in the root project directory.

To build the documentation yourself, after installing requirements.txt, run:

::

  $ pip install sphinx
  $ cd docs/
  $ make html

License
-------

MIT licensed. See the `LICENSE
file <https://github.com/goldsmith/Wikipedia/blob/master/LICENSE>`__ for
full details.

Credits
-------

-  `wiki-api <https://github.com/richardasaurus/wiki-api>`__ by
   @richardasaurus for inspiration
-  @nmoroze and @themichaelyang for feedback and suggestions
-  The `Wikimedia
   Foundation <http://wikimediafoundation.org/wiki/Home>`__ for giving
   the world free access to data



.. image:: https://d2weczhvl823v0.cloudfront.net/goldsmith/wikipedia/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

