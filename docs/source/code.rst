.. _api:

API reference
=============

Here you can find the full developer API for the wikipedia project.

.. automodule:: wikipedia
   :members: search, suggest, summary, page, geosearch, languages, set_lang, set_user_agent, set_timeout, set_rate_limiting, random, donate

.. autoclass:: wikipedia.WikipediaPage
   :members:

Exceptions
----------

.. automodule:: wikipedia.exceptions
   :members: WikipediaException, RequestError, PageError, DisambiguationError, RedirectError, HTTPTimeoutError

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
