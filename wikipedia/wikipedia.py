import requests
from bs4 import BeautifulSoup

__all__ = ["search", "page", "suggest", "WikipediaPage"]

def search(query, results=10):

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

	if auto_suggest:
		title = suggest(title) or title
	
	return WikipediaPage(title)

class WikipediaPage(object):

	def __init__(self, title):
		self.title = title

		self.load()

	def load(self):
		search_params = {
			"action": "parse",
		}
		search_params['page'] = self.title
	
		self._raw = _wiki_request(**search_params)
		self.html = self._raw["parse"]["text"]["*"]

	@property
	def content(self):
		html = BeautifulSoup(self.html)
		paragraphs = html.find_all("p")

		for p in paragraphs:
			for sup in p.find_all("sup"):
				sup.extract()
		
		return '\n\n'.join(p.get_text() for p in paragraphs)	

def _wiki_request(**params):
	"""
	Makes a request to the Wikipedia API using the given search parameters. Returns a dict of the JSON data returned.
	"""
	api_url = "http://en.wikipedia.org/w/api.php"
	params['format'] = "json"

	r = requests.get(api_url, params=params)
	return r.json()