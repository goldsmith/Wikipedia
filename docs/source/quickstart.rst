.. _quickstart:

Quickstart
**********

Start using wikipedia for Python in less than 5 minutes! If you are
looking for the the full developer API, see :ref:`api`.

Begin by installing wikipedia (version 1.5 requires Python 3.10 or
newer)::

	$ pip install wikipedia

Wikipedia asks that API clients introduce themselves, so before making
requests, tell us a little about your application::

	>>> import wikipedia

	>>> wikipedia.set_user_agent("my-cool-project/1.0 (https://example.com/contact)")

Now let's use search and suggestion.

As you might guess,
``wikipedia.search`` does a Wikipedia search for a query,
and ``wikipedia.suggest`` returns the suggested Wikipedia title for a
query, or ``None``::

	>>> wikipedia.search("Barack")
	['Barack Obama', 'Barack Obama Sr.', 'Barack (disambiguation)', 'Family of Barack Obama', 'Barack Obama (disambiguation)', 'Zach Barack', 'Barack (name)', 'President Barack Obama (painting)', 'Presidency of Barack Obama', 'Ann Dunham']

	>>> wikipedia.suggest("Barak Obama")
	'barack obama'

We can also get fewer or more results by using the ``results`` kwarg::

	>>> wikipedia.search("Ford", results=3)
	['Ford', 'Gerald Ford', 'Harrison Ford']

To get the summary of an article, use ``wikipedia.summary``::

	>>> wikipedia.summary("GitHub")
	'GitHub is a proprietary developer platform that allows developers to create, store, manage, and share their code...'

	>>> wikipedia.summary("Apple III", sentences=1)
	'The Apple III (stylized as apple ///) is a business-oriented personal computer that was produced by Apple Computer and released in 1980.'

But watch out - ``wikipedia.summary`` will raise a
``DisambiguationError`` if the page is a disambiguation page, or a
``PageError`` if the page doesn't exist (although by default, it tries to
find the page you meant with ``suggest`` and ``search``.)::

	>>> wikipedia.summary("Mercury")
	Traceback (most recent call last):
	...
	wikipedia.exceptions.DisambiguationError: "Mercury" may refer to:
	Mercury (planet)
	Mercury (element)
	Mercury (mythology)
	...

	>>> try:
	... 	mercury = wikipedia.summary("Mercury")
	... except wikipedia.exceptions.DisambiguationError as e:
	... 	print(e.options)
	...
	['Mercury (planet)', 'Mercury (element)', 'Mercury (mythology)', 'Mercury (toy manufacturer)', 'Mercury Communications', ...]

	>>> wikipedia.summary("zxqjvbn")
	Traceback (most recent call last):
	...
	wikipedia.exceptions.PageError: "zxqjvbn" does not match any pages. Try another query!

``wikipedia.page`` enables you to load and access data from full Wikipedia
pages. Initialize with a page title (keep in mind the errors listed
above), and then access most properties using property methods::

	>>> ny = wikipedia.page("New York City")

	>>> ny.title
	'New York City'

	>>> ny.url
	'https://en.wikipedia.org/wiki/New_York_City'

	>>> ny.content
	'New York, often called New York City (NYC), is the most populous city in the United States. ...

	>>> ny.images[0]
	'https://upload.wikimedia.org/wikipedia/commons/3/3f/1232-42_Dean_Street_Crown_Heights.jpg...'

	>>> ny.links[0]
	'116 John Street'

To change the language of the Wikipedia you are accessing, use
``wikipedia.set_lang``. Remember to search for page titles in the language
that you have set, not English! Pages you already loaded stick with the
language you fetched them in, which is a fancy way of saying ``ny`` up
there is still English::

	>>> wikipedia.set_lang("fr")

	>>> print(wikipedia.summary("Facebook", sentences=1))
	Facebook [ˈfeɪs.bʊk] (litt. ...

To get a list of all possible language prefixes, try::

	>>> 'en' in wikipedia.languages()
	True
	>>> print(wikipedia.languages()['es'])
	español

A couple of things you get for free: requests go over HTTPS, time out
after 5 seconds connecting and 15 seconds reading (change that with
``set_timeout``), and retry transient failures twice before giving up with
a ``RequestError`` or ``HTTPTimeoutError``. If you're making a lot of
requests, ``wikipedia.set_rate_limiting(True)`` keeps at least 50
milliseconds between them — Wikipedia thanks you.

Finally, the last method you're going to want to know in the wikipedia
module is ``wikipedia.donate``::

	>>> wikipedia.donate()
	# your favorite web browser will open to the donations page of the Wikimedia project
	# because without them, none of this would be possible

See :ref:`api` for a full reference to the rest of the arguments and
methods you can use!

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
