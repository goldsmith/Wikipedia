Wikipedia
=========

**Wikipedia** is a Python library that makes it easy to access and parse
data from Wikipedia.

Search Wikipedia, get article summaries, get data like links and images
from a page, and more. Wikipedia wraps the `MediaWiki
API <https://www.mediawiki.org/wiki/API>`__ so you can focus on using
Wikipedia data, not getting it.

.. code:: python

  >>> import wikipedia
  >>> wikipedia.summary("Wikipedia", sentences=1)
  'Wikipedia is a free online encyclopedia written and maintained by a community of volunteer editors, known as Wikipedians...'

  >>> wikipedia.search("Barack")
  ['Barack Obama', 'Barack Obama Sr.', 'Barack (disambiguation)', 'Family of Barack Obama', ...]

  >>> ny = wikipedia.page("New York City")
  >>> ny.title
  'New York City'
  >>> ny.url
  'https://en.wikipedia.org/wiki/New_York_City'
  >>> ny.content
  'New York, often called New York City (NYC), is the most populous city in the United States...'
  >>> ny.links[0]
  '116 John Street'

  >>> wikipedia.set_lang("fr")
  >>> wikipedia.summary("Facebook", sentences=1)
  'Facebook [ˈfeɪs.bʊk] (litt. ...'

Installation
------------

To install Wikipedia, simply run:

::

  $ pip install wikipedia

Wikipedia 1.5 supports Python 3.10 and newer. If you're still on an older
Python, ``pip install "wikipedia<1.5"`` will keep working the way it
always has.

Documentation
-------------

Read the docs at https://wikipedia.readthedocs.io/.

-  `Quickstart <https://wikipedia.readthedocs.io/en/latest/quickstart.html>`__
-  `Full API <https://wikipedia.readthedocs.io/en/latest/code.html>`__

Playing nicely with Wikipedia
-----------------------------

One small thing before you script away: Wikimedia asks that API clients
say who they are, so please set a user agent with a way to reach you:

.. code:: python

  >>> wikipedia.set_user_agent("my-cool-project/1.0 (https://example.com/contact)")

The library takes care of the rest: requests go over HTTPS, share a
connection pool, give up after a 5-second connect / 15-second read timeout
(``set_timeout`` if you want different limits), and retry transient
failures at most twice before raising ``RequestError`` or
``HTTPTimeoutError``. ``set_rate_limiting(True)`` keeps at least 50 ms
between requests if you want to be extra polite. Results are cached for
five minutes so asking twice doesn't cost Wikipedia a dime.

Note: this library was designed for ease of use and simplicity, not for
advanced use. If you plan on doing serious scraping or automated requests,
please use `Pywikibot <https://www.mediawiki.org/wiki/Manual:Pywikibot>`__
(or one of the other more advanced `Python MediaWiki API wrappers
<https://en.wikipedia.org/wiki/Wikipedia:Creating_a_bot#Python>`__), which
has a larger API, rate limiting, and other features so we can be
considerate of the MediaWiki infrastructure.

What's new in 1.5
-----------------

Thirteen years of gentle maintenance, collected: exact titles resolve
before suggestions, disambiguation pages raise instead of silently
picking a different article for you, redirects and sections behave,
missing properties return ``[]`` or ``None`` instead of exploding, and
page objects remember which language you fetched them in. Python 3.10+
only, real packaging, and an offline test suite that doesn't hammer the
API. See ``CHANGELOG.md`` for the full list and ``CONTRIBUTIONS.md`` for
the many people whose pull requests informed it.

Development
-----------

To run tests, clone the `repository on GitHub
<https://github.com/goldsmith/Wikipedia>`__, then run:

::

  $ pip install -e '.[dev]'
  $ bash runtests

The test suite runs offline — it stubs HTTP rather than pestering
Wikipedia. ``python scripts/live_smoke.py`` runs the opt-in live checks
against the real API (rate limited, capped at 30 requests), and
``pip install -e '.[docs]'`` plus ``sphinx -b html docs/source
docs/_build/html`` builds the documentation.

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
   Foundation <https://wikimediafoundation.org/>`__ for giving
   the world free access to data
