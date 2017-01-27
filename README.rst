MediaWikiAPI
===================

.. image:: https://travis-ci.org/lehinevych/MediaWikiAPI.svg?branch=master
  :target: https://travis-ci.org/leginevych/MediaWikiAPI



**MediaWikiAPI** is a Python library that makes it easy to access and parse
data from Wikipedia.

Search Wikipedia, get article summaries, get data like links and images
from a page, and more. Wikipedia wraps the `MediaWiki
API <https://www.mediawiki.org/wiki/API>`__ so you can focus on using
Wikipedia data, not getting it.

.. code:: python

  >>> import mediawikiapi
  >>> print mediawikiapi.summary("Wikipedia")
  # Wikipedia (/ˌwɪkɨˈpiːdiə/ or /ˌwɪkiˈpiːdiə/ WIK-i-PEE-dee-ə) is a collaboratively edited, multilingual, free Internet encyclopedia supported by the non-profit Wikimedia Foundation...

  >>> mediawikiapi.search("Barack")
  # [u'Barak (given name)', u'Barack Obama', u'Barack (brandy)', u'Presidency of Barack Obama', u'Family of Barack Obama', u'First inauguration of Barack Obama', u'Barack Obama presidential campaign, 2008', u'Barack Obama, Sr.', u'Barack Obama citizenship conspiracy theories', u'Presidential transition of Barack Obama']

  >>> ny = mediawikiapi.page("New York")
  >>> ny.title
  # u'New York'
  >>> ny.url
  # u'http://en.wikipedia.org/wiki/New_York'
  >>> ny.content
  # u'New York is a state in the Northeastern region of the United States. New York is the 27th-most exten'...
  >>> ny.links[0]
  # u'1790 United States Census'

  >>> mediawikiapi.set_lang("fr")
  >>> mediawikiapi.summary("Facebook", sentences=1)
  # Facebook est un service de réseautage social en ligne sur Internet permettant d'y publier des informations (photographies, liens, textes, etc.) en contrôlant leur visibilité par différentes catégories de personnes.


Installation
------------

To install MediaWikiAPI, simply run:

::

  $ pip install mediawikiapi

MediaWikiAPI is compatible only with Python 3.3+. Support for Python 2.7 will be added soon.

Documentation
-------------

Soon will be available on readthedocs.

To run tests, clone the `repository on GitHub <https://github.com/lehinevych/MediaWikiAPI>`__, then run:

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
file <https://github.com/lehinevych/MediaWikiAPI/blob/master/LICENSE>`__ for
full details.

Credits
-------
-  @goldsmith for making such a fantastic library to fork