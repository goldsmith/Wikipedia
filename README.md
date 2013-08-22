Wikipedia
=========

**Wikipedia** is a Python library that makes it easy to access and parse data from Wikipedia.

Search Wikipedia, get article summaries, get data like links and images from a page, and more. Wikipedia wraps the [MediaWiki API](https://www.mediawiki.org/wiki/API) so you can focus on using Wikipedia data, not getting it.

```python
	import wikipedia
	print wikipedia.summary("Wikipedia")
	# Wikipedia (/ˌwɪkɨˈpiːdiə/ or /ˌwɪkiˈpiːdiə/ WIK-i-PEE-dee-ə) is a collaboratively edited, multilingual, free Internet encyclopedia supported by the non-profit Wikimedia Foundation...
	
	wikipedia.search("Barack")
	# [u'Barak (given name)', u'Barack Obama', u'Barack (brandy)', u'Presidency of Barack Obama', u'Family of Barack Obama', u'First inauguration of Barack Obama', u'Barack Obama presidential campaign, 2008', u'Barack Obama, Sr.', u'Barack Obama citizenship conspiracy theories', u'Presidential transition of Barack Obama']
	
	ny = wikipedia.page("New York")
	ny.title
	# u'New York'
	ny.url
	# u'http://en.wikipedia.org/wiki/NewYork'
	ny.content
	# u'New York is a state in the Northeastern region of the United States. New York is the 27th-most exten'...
	ny.links[0]
	# u'1790 United States Census'
```
	
Installation
------------

To install Wikipedia, simply run:

	$ pip install wikipedia
	
Documentation
-------------

Read the docs at https://wikipedia.readthedocs.org/en/latest/.

* [Quickstart](https://wikipedia.readthedocs.org/en/latest/quickstart.html)
* [Full API](https://wikipedia.readthedocs.org/en/latest/code.html)

License
-------

MIT licensed. See the [LICENSE file](https://github.com/goldsmith/Wikipedia/blob/master/LICENSE) for full details.

Credits
-------

* [wiki-api](https://github.com/richardasaurus/wiki-api) by @richardasaurus for inspiration
* @nmoroze and @themichaelyang for feedback and suggestions
* The [Wikimedia Foundation](http://wikimediafoundation.org/wiki/Home) for giving the world free access to data
