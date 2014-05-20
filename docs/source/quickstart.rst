.. _quickstart:

Quickstart
**********

Start using wikipedia for Python in less than 5 minutes! If you are looking for the the full developer API, see :ref:`api`.

Begin by installing wikipedia::

	$ pip install wikipedia

Now let's use search and suggestion.

As you might guess,
``wikipedia.search`` does a Wikipedia search for a query,
and ``wikipedia.suggest`` returns the suggested Wikipedia title for a query, or ``None``::

	>>> import wikipedia

	>>> wikipedia.search("Barack")
	[u'Barak (given name)', u'Barack Obama', u'Barack (brandy)', u'Presidency of Barack Obama', u'Family of Barack Obama', u'First inauguration of Barack Obama', u'Barack Obama presidential campaign, 2008', u'Barack Obama, Sr.', u'Barack Obama citizenship conspiracy theories', u'Presidential transition of Barack Obama']

	>>> wikipedia.suggest("Barak Obama")
	u'Barack Obama'

We can also get fewer or more results by using the ``results`` kwarg::

	>>> wikipedia.search("Ford", results=3)
	[u'Ford Motor Company', u'Gerald Ford', u'Henry Ford']

To get the summary of an article, use ``wikipedia.summary``::

	>>> wikipedia.summary("GitHub")
	2011, GitHub was the most popular open source code repository site.\nGitHub Inc. was founded in 2008 and is based in San Francisco, California.\nIn July 2012, the company received $100 million in Series A funding, primarily from Andreessen Horowitz.'

	>>> wikipedia.summary("Apple III", sentences=1)
	u'The Apple III (often rendered as Apple ///) is a business-oriented personal computer produced and released by Apple Computer that was intended as the successor to the Apple II series, but largely considered a failure in the market. '

But watch out - ``wikipedia.summary`` will raise a ``DisambiguationError`` if the page is a disambiguation page, or a ``PageError`` if the page doesn't exist (although by default, it tries to find the page you meant with ``suggest`` and ``search``.)::

	>>> wikipedia.summary("Mercury")
	Traceback (most recent call last):
	...
	wikipedia.exceptions.DisambiguationError: "Mercury" may refer to:
	Mercury (mythology)
	Mercury (planet)
	Mercury (element)

	>>> try:
	... 	mercury = wikipedia.summary("Mercury")
	... except wikipedia.exceptions.DisambiguationError as e:
	... 	print e.options
	...
	[u'Mercury (mythology)', u'Mercury (planet)', u'Mercury (element)', u'Mercury, Nevada', ...]

	>>> wikipedia.summary("zvv")
	Traceback (most recent call last):
	...
	wikipedia.exceptions.PageError: "zvv" does not match any pages. Try another query!

``wikipedia.page`` enables you to load and access data from full Wikipedia pages. Initialize with a page title (keep in mind the errors listed above), and then access most properties using property methods::

	>>> ny = wikipedia.page("New York")

	>>> ny.title
	u'New York'

	>>> ny.url
	u'http://en.wikipedia.org/wiki/NewYork'

	>>> ny.content
	u'New York is a state in the Northeastern region of the United States. New York is the 27th-most exten'...

	>>> ny.images[0]
	u'http://upload.wikimedia.org/wikipedia/commons/9/91/New_York_quarter%2C_reverse_side%2C_2001.jpg'

	>>> ny.links[0]
	u'1790 United States Census'

To change the language of the Wikipedia you are accessing, use ``wikipedia.set_lang``. Remember to search for page titles in the language that you have set, not English!::

	>>> wikipedia.set_lang("fr")

	>>> print wikipedia.summary("Francois Hollande")
	François Hollande, né le 12 août 1954 à Rouen, en Seine-Maritime, est un homme d'État français. Il est président de la République française depuis le 15 mai 2012...

To get a list of all possible language prefixes, try:

	>>> 'en' in wikipedia.languages()
	True
	>>> print wikipedia.languages()['es']
	español

Finally, the last method you're going to want to know in the wikipedia module is ``wikipedia.donate``::

	>>> wikipedia.donate()
	# your favorite web browser will open to the donations page of the Wikimedia project
	# because without them, none of this would be possible

See :ref:`api` for a full reference to the rest of the arguments and methods you can use!

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
