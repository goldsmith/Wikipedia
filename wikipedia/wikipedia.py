import requests
from bs4 import BeautifulSoup

__all__ = ["search", "page", "suggest", "WikipediaPage"]

def search(query, results=10):
	"""
	Do a Wikipedia search and return a list of at most `result` results.
	"""

	search_params = {
		"action": "query",
		"list": "search",
		"srprop": "",
	}
	search_params["srsearch"] = query
	search_params["limit"] = results

	raw_results 	= _wiki_request(**search_params)
	search_results 	= (d['title'] for d in raw_results['query']['search'])

	return list(search_results)

def suggest(query):
	"""
	Get a Wikipedia search suggestion for `query`.
	Returns a string or None if no suggestion was found.
	"""

	search_params = {
		"action": "query",
		"list": "search",
		"srinfo": "suggestion",
		"srprop": "",
	}
	search_params['srsearch'] = query

	raw_result = _wiki_request(**search_params)

	if raw_result['query'].get('searchinfo'):
		return raw_result['query']['searchinfo']['suggestion']

	return None

def page(title, auto_suggest=True):
	"""
	Get a WikipediaPage object for the page with title `title`.

	Keyword arguments:
	auto_suggest - if True, replace title with a Wikipedia suggested alternative
	"""

	if auto_suggest:
		title = suggest(title) or title
	
	return WikipediaPage(title)

class WikipediaPage(object):
	"""
	Contains data from a Wikipedia page.
	Uses property methods to filter data from the raw HTML.
	"""

	def __init__(self, title):
		self.title = title

		self.load()

	def load(self):
		"""Make a request to Wikipedia and load the page HTML into memory."""

		search_params = {
			"action": "parse",
		}
		search_params['page'] = self.title
	
		self._raw = _wiki_request(**search_params)
		self.html = self._raw["parse"]["text"]["*"]

	@property
	def content(self):
		"""
		Get the plain text content of the page, excluding images, tables, and other data.
		"""
		html = BeautifulSoup(self.html)
		paragraphs = html.find_all("p")

		for p in paragraphs:
			for sup in p.find_all("sup"):
				sup.extract()
		
		return '\n\n'.join(p.get_text() for p in paragraphs)	

def _wiki_request(**params):
	"""
	Make a request to the Wikipedia API using the given search parameters. 
	Returns a parsed dict of the JSON response.
	"""
	api_url = "http://en.wikipedia.org/w/api.php"
	params['format'] = "json"

	r = requests.get(api_url, params=params)
	return r.json()