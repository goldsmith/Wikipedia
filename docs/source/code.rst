.. _api:

MediaWikiAPI Documentation
***********************

Here you can find the full developer API for the MediaWikiAPI project.

Contents:

.. toctree::

   code

.. automodule:: wikipedia
  :members:

Functions and Classes
===============================

.. automodule:: mediawikiapi

  .. autofunction:: search(query, results=10, suggestion=False)

  .. autofunction:: suggest(query)

  .. autofunction:: summary(query, sentences=0, chars=0, auto_suggest=True, redirect=True)

  .. autofunction:: page

  .. autofunction:: geosearch(latitude, longitude, title=None, results=10, radius=1000)

.. autoclass:: mediawikiapi.WikipediaPage
  :members:

.. autofunction:: mediawikiapi.languages

.. autofunction:: mediawikiapi.set_lang

.. autofunction:: mediawikiapi.config.set_rate_limiting

.. autofunction:: mediawikiapi.random

.. autofunction:: mediawikiapi.donate

Exceptions
==========

.. automodule:: mediawikiapi.exceptions
  :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`