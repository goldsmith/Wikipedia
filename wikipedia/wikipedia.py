import requests
from bs4 import BeautifulSoup

from .exceptions import *

__all__ = ["search", "page", "suggest", "WikipediaPage"]

def search(query, results=10, suggestion=False):
	"""
	Do a Wikipedia search for `query`.

	Keyword arguments:
	results - the maxmimum number of results returned
	suggestion - if True, return results and suggestion (if any) in a tuple
	"""

	search_params = {
		"list": "search",
		"srprop": "",
		"srlimit": results
	}
	if suggestion:
		search_params["srinfo"] = "suggestion"
	search_params["srsearch"] = query
	search_params["limit"] = results

	raw_results 	= _wiki_request(**search_params)
	search_results 	= (d['title'] for d in raw_results['query']['search'])

	if suggestion:
		if raw_results['query'].get('searchinfo'):
			return list(search_results), raw_results['query']['searchinfo']['suggestion']
		else:
			return list(search_results), None

	return list(search_results)

def suggest(query):
	"""
	Get a Wikipedia search suggestion for `query`.
	Returns a string or None if no suggestion was found.
	"""

	search_params = {
		"list": "search",
		"srinfo": "suggestion",
		"srprop": "",
	}
	search_params['srsearch'] = query

	raw_result = _wiki_request(**search_params)

	if raw_result['query'].get('searchinfo'):
		return raw_result['query']['searchinfo']['suggestion']

	return None

def page(title, auto_suggest=True, redirect=True):
	"""
	Get a WikipediaPage object for the page with title `title`.

	Keyword arguments:
	auto_suggest - let Wikipedia find a valid page title for the query
	redirect - allow redirection without raising RedirectError
	"""

	if auto_suggest:
		results, suggestion = search(title, results=1, suggestion=True)
		try:
			title = suggestion or results[0]
		except IndexError:
			# if there is no suggestion or search results, the page doesn't exist
			raise PageError(title)
	
	return WikipediaPage(title, redirect=redirect)

class WikipediaPage(object):
	"""
	Contains data from a Wikipedia page.
	Uses property methods to filter data from the raw HTML.
	"""

	def __init__(self, title, redirect=True, original_title=""):
		self.title = title
		self.original_title = original_title or title

		self.load(redirect=redirect)

	def load(self, redirect=True):
		"""
		Load basic information from Wikipedia. 
		Confirm that page exists and is not a disambiguation/redirect.
		"""

		query_params = {
			'prop': "info|categories",
			'inprop': "url",
			'clcategories': "Category:All disambiguation pages",
			'titles': self.title
		}
	
		request = _wiki_request(**query_params)
		pageid = request['query']['pages'].keys()[0]
		data = request['query']['pages'][pageid]

		# missing is equal to empty string if it is True
		if data.get('missing') == "":
			raise PageError(self.title)

		# same thing for redirect
		elif data.get('redirect') == "":
			if redirect:
				# change the title and reload the whole object
				query_params = {
					'prop': "extracts",
					'explaintext': "",
					'titles': self.title
				}

				request = _wiki_request(**query_params)
				title = ' '.join(request['query']['pages'][pageid]['extract'].split()[1:])

				self.__init__(title, redirect=redirect)

			else:
				raise RedirectError(self.title)

		# since we limited categories, if a category is returned 
		# then the page must be a disambiguation page
		elif data.get('categories'):
			request = _wiki_request(titles=self.title, prop="revisions", rvprop="content", rvparse="", rvlimit=1)
			html = request['query']['pages'][pageid]['revisions'][0]['*']

			may_refer_to = [li.a.get_text() for li in BeautifulSoup(html).ul.find_all('li')]
			raise DisambiguationError(self.title, may_refer_to)

		else:
			self.pageid = pageid
			self.url = data['fullurl']

	def content(self):
		"""
		Plain text content of the page, excluding images, tables, and other data.
		"""

		if not getattr(self, "_content", False):
			query_params = {
				'prop': "extracts",
				'explaintext': "",
				'titles': self.title
			}

			request = _wiki_request(**query_params)
			self._content = content = request['query']['pages'][self.pageid]['extract']

		return self._content

	def summary(self, sentences=0, chars=0):
		"""
		Plain text summary of the page.

		Keyword arguments:
		sentences - if set, return the first `sentences` sentences
		chars - if set, return only the first `chars` characters.
		"""

		# cache the most common form of invoking summary
		if not sentences and not chars and getattr(self, "_summary", False):
			return self._summary

		query_params = {
			'prop': "extracts",
			'explaintext': "",
			'titles': self.title
		}

		if sentences:
			query_params['exsentences'] = sentences
		elif chars:
			query_params['exchars'] = chars
		else:
			query_params['exintro'] = ""

		request = _wiki_request(**query_params)
		summary = request['query']['pages'][self.pageid]['extract']

		if not sentences and not chars:
			self._summary = summary

		return summary

	def images(self):
		"""
		List of URLs of images on the page.
		"""	

		if not getattr(self, "_images", False):
			query_params = {
				'generator': "images",
				'gimlimit': "max",
				'prop': "imageinfo",
				'iiprop': "url",
				'titles': self.title,
			}
	
			request = _wiki_request(**query_params)
	
			image_keys = request['query']['pages'].keys()
			images = (request['query']['pages'][key] for key in image_keys)
			self._images = [image['imageinfo'][0]['url'] for image in images if image.get('imageinfo')]

		return self._images

	def references(self):
		"""
		List of URLs of external links on a page.
		May include external links within page that aren't technically cited anywhere.
		"""

		if not getattr(self, "_references", False):
			query_params = {
				'prop': "extlinks",
				'ellimit': "max",
				'titles': self.title,
			}

			request = _wiki_request(**query_params)

			links = request['query']['pages'][self.pageid]['extlinks']
			relative_urls = (link['*'] for link in links)

			def add_protocol(url):
				return url if url.startswith('http') else 'http:' + url

			self._references = [add_protocol(url) for url in relative_urls]

		return self._references

def _wiki_request(**params):
	"""
	Make a request to the Wikipedia API using the given search parameters. 
	Returns a parsed dict of the JSON response.
	"""
	api_url = "http://en.wikipedia.org/w/api.php"
	params['format'] = "json"
	params['action'] = "query"

	r = requests.get(api_url, params=params)
	return r.json()