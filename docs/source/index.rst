.. _index:

Wikipedia
=========

Wikipedia is a Python library that makes it easy to access and parse data
from Wikipedia.

Search Wikipedia, get article summaries, get data like links and images
from a page, and more. Wikipedia wraps the `MediaWiki API
<https://www.mediawiki.org/wiki/API>`_ so you can focus on using Wikipedia
data, not getting it.

::

	>>> import wikipedia

	>>> print(wikipedia.summary("Wikipedia", sentences=1))
	Wikipedia is a free online encyclopedia written and maintained by a community of volunteer editors, known as Wikipedians...

Go to the :ref:`quickstart` to start using ``wikipedia`` now, or see the
:ref:`api`.

These docs describe version 1.5, which requires Python 3.10 or newer.

.. toctree::
   :maxdepth: 2
   :hidden:

   quickstart
   code

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
