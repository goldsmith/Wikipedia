.. _api:

Wikipedia Documentation
***********************

Here you can find the full developer API for the wikipedia project.

Contents:

.. toctree::

   code

.. automodule:: wikipedia
	:members:

Functions and Classes
===============================

.. automodule:: wikipedia

	.. autofunction:: search(query, results=10, suggestion=False)

	.. autofunction:: suggest(query)

	.. autofunction:: summary(query, sentences=0, chars=0, auto_suggest=True, redirect=True)

	.. autofunction:: page

.. autoclass:: wikipedia.WikipediaPage
	:members:

.. autofunction:: wikipedia.random

.. autofunction:: wikipedia.donate

Exceptions
==========

.. automodule:: wikipedia.exceptions
	:members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`