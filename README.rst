Wikipedia
=========

**Wikipedia** is a small synchronous Python library for searching Wikipedia,
reading article text, and retrieving page metadata.

Installation
------------

This branch contains an **unreleased 1.5.0 candidate**. To try the examples below,
install from a checkout of this branch in a virtual environment:

::

   python -m pip install .

``python -m pip install wikipedia`` installs the latest published release,
currently 1.4.0, which does not include the new APIs or behavior described here.

The proposed 1.5 series supports Python 3.10–3.14. Python 2 and Python 3.9 and
older are no longer supported.

Quick start
-----------

.. code-block:: python

   import wikipedia

   # Replace this example URL with your application's contact page.
   wikipedia.set_user_agent("MyApplication/1.0 (https://example.org/contact)")
   wikipedia.set_timeout((5, 15))
   wikipedia.set_lang("en")

   titles = wikipedia.search("Earth", results=3)
   earth = wikipedia.page("Earth")
   print(earth.title, earth.url)
   print(earth.summary)
   print(earth.sections)

   wikipedia.set_lang("fr")
   print(wikipedia.summary("Terre", sentences=2))
   # The existing earth object still fetches from English Wikipedia.

Exact titles are resolved before trying search suggestions. Set
``auto_suggest=False`` to disable the fallback. An exact disambiguation page
raises ``DisambiguationError``; it is not silently replaced by another article.

.. code-block:: python

   try:
       article = wikipedia.page("Mercury", auto_suggest=False)
   except wikipedia.DisambiguationError as error:
       print(error.options)
   except wikipedia.PageError as error:
       print(error)
   except wikipedia.HTTPTimeoutError as error:
       print(error)
   except wikipedia.RequestError as error:
       print(error.status_code, error.api_code, error.retry_after)

Requests and caching
--------------------

Requests use HTTPS, a shared connection pool, and a default connect/read timeout
of ``(5, 15)`` seconds. ``set_timeout(10)`` applies ten seconds to both phases;
``set_timeout(None)`` explicitly disables timeouts. A read timeout limits socket
inactivity, not total operation time. A page property can require several requests.

Transient failures receive at most two retries per request. Server retry delays
are respected, with a total retry-sleep budget of 30 seconds per request. Longer
server delays raise ``RequestError`` with ``retry_after`` instead of retrying early.
Permanent HTTP/API failures and malformed responses raise ``RequestError``;
exhausted timeouts raise ``HTTPTimeoutError``. Both inherit ``WikipediaException``.

Set an informative application user agent with contact information, as required
by `Wikimedia's API guidance <https://www.mediawiki.org/wiki/API:Etiquette>`_.
``set_rate_limiting(True)`` spaces requests by at least 50 milliseconds; supply
``min_wait=datetime.timedelta(...)`` for a longer interval. Make automated requests
serially and respect server limits. Requests' standard proxy environment variables
(``HTTPS_PROXY``, ``HTTP_PROXY``, ``NO_PROXY``) remain supported.

Cached module functions hold at most 256 entries each, expiring after five minutes.
Language is part of their keys, and ``set_lang`` clears them. Call, for example,
``wikipedia.search.clear_cache()`` to clear a function's cache manually. Returned
lists and dictionaries can be edited without changing cached results. A page
object caches fetched properties for its lifetime, including empty results.

Configuration remains process-wide. Changing language, timeout, rate limit, or user
agent concurrently with requests is not supported. This is not a thread-safe client
architecture. Use separate processes for independently configured concurrent workloads.

Content and compatibility
-------------------------

``content`` and ``summary`` use MediaWiki's plain-text extracts, which omit tables,
images and some other markup. Sentence and character limits use the upstream
extract API and are approximate. ``section(name)`` returns text through the next
heading, excluding subsections; a missing section returns ``None``.

``links`` and ``images`` follow the API's order, not article display order.
``references`` means external links, including links that are not citations.
Missing list properties return ``[]``; missing coordinates return ``None``.
Coordinates remain a tuple of ``Decimal`` values. ``random(1)`` returns a string;
multiple random pages return a list. ``__version__`` remains a three-item tuple.
The existing positional function signatures are preserved.

See ``CHANGELOG.md`` for intentional changes from 1.4.0 and ``CONTRIBUTIONS.md``
for PR attribution. This release does not add async support, translation lookup,
infoboxes, tables, category-member traversal, or a new client API.

Development
-----------

::

   python -m pip install -e '.[dev,docs]'
   python -m pytest
   python -m ruff check wikipedia tests scripts
   python -m build
   python -m twine check dist/*
   python scripts/check_distributions.py
   python -m sphinx -W --keep-going -b html docs/source docs/_build/html

The default test suite is offline and blocks unexpected HTTP calls. The optional
LangChain integration test uses ``langchain-community==0.4.2`` and synthetic HTTP
responses. ``python scripts/live_smoke.py`` runs the separate opt-in live checks,
with a persistent budget of at most 30 requests per budget file.

Documentation
-------------

The public documentation is at https://wikipedia.readthedocs.io/.
Build locally to inspect documentation for this unreleased branch.

License and credits
-------------------

MIT licensed; see ``LICENSE``. Original author: Jonathan Goldsmith.

Thanks to ``wiki-api`` by @richardasaurus for inspiration, @nmoroze and
@themichaelyang for feedback, the project's contributors, and the Wikimedia
Foundation and volunteers who make Wikipedia possible.
