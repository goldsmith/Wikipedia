Wikipedia with sections
=======================

**Wikipedia with sections** is a Python library that makes it easy to access and parse
data from Wikipedia.

This is a fork from Jonathan Goldsmith's `Wikipedia package <https://github.com/goldsmith/Wikipedia>`__

.. code:: python

  >>> import wikipedia

  >>> ny = wikipedia.page("New York")
  >>> ny.sections[:5]
  # ['Etymology', 'History', 'Early history', 'Dutch rule', 'English rule']


Installation
------------

To install Wikipedia, simply run:

::

  $ pip install wikipedia_sections

Wikipedia is compatible with Python 2.6+ (2.7+ to run unittest discover) and Python 3.3+.

Documentation
-------------

See https://github.com/goldsmith/Wikipedia for full dcumentation.

License
-------

MIT licensed. See the `LICENSE
file <https://github.com/sachavakili/Wikipedia/blob/master/LICENSE>`__ for
full details.

Credits
-------

-  `Wikipedia <https://github.com/goldsmith/Wikipedia>`__ by Jonathan Goldsmith for the original repository
-  `wiki-api <https://github.com/richardasaurus/wiki-api>`__ by
   @richardasaurus for inspiration
-  @nmoroze and @themichaelyang for feedback and suggestions
-  The `Wikimedia
   Foundation <http://wikimediafoundation.org/wiki/Home>`__ for giving
   the world free access to data
