from __future__ import unicode_literals

import time
from bs4 import BeautifulSoup
from .exceptions import (
  PageError, HTTPTimeoutError, MediaWikiAPIException
)
from .config import Configuration
from .language import Language
from .util import cache
from .wikipediapage import WikipediaPage, _wiki_request

config = Configuration(lang=Language())

def set_lang(lang):
  config.set_lang(lang)
  for cached_func in (search, suggest, summary):
    cached_func.clear_cache()
  

@cache
def search(query, results=10, suggestion=False):
  '''
  Do a Wikipedia search for `query`.

  Keyword arguments:

  * results - the maxmimum number of results returned
  * suggestion - if True, return results and suggestion (if any) in a tuple
  '''

  search_params = {
    'list': 'search',
    'srprop': '',
    'srlimit': results,
    'limit': results,
    'srsearch': query
  }
  if suggestion:
    search_params['srinfo'] = 'suggestion'

  raw_results = _wiki_request(search_params)

  if 'error' in raw_results:
    if raw_results['error']['info'] in ('HTTP request timed out.', 'Pool queue is full'):
      raise HTTPTimeoutError(query)
    else:
      raise MediaWikiAPIException(raw_results['error']['info'])

  search_results = (d['title'] for d in raw_results['query']['search'])

  if suggestion:
    if raw_results['query'].get('searchinfo'):
      return list(search_results), raw_results['query']['searchinfo']['suggestion']
    else:
      return list(search_results), None

  return list(search_results)


@cache
def geosearch(latitude, longitude, title=None, results=10, radius=1000):
  '''
  Do a wikipedia geo search for `latitude` and `longitude`
  using HTTP API described in http://www.mediawiki.org/wiki/Extension:GeoData

  Arguments:

  * latitude (float or decimal.Decimal)
  * longitude (float or decimal.Decimal)

  Keyword arguments:

  * title - The title of an article to search for
  * results - the maximum number of results returned
  * radius - Search radius in meters. The value must be between 10 and 10000
  '''

  search_params = {
    'list': 'geosearch',
    'gsradius': radius,
    'gscoord': '{0}|{1}'.format(latitude, longitude),
    'gslimit': results
  }
  if title:
    search_params['titles'] = title

  raw_results = _wiki_request(search_params)

  if 'error' in raw_results:
    if raw_results['error']['info'] in ('HTTP request timed out.', 'Pool queue is full'):
      raise HTTPTimeoutError('{0}|{1}'.format(latitude, longitude))
    else:
      raise MediaWikiAPIException(raw_results['error']['info'])

  search_pages = raw_results['query'].get('pages', None)
  if search_pages:
    search_results = (v['title'] for k, v in search_pages.items() if k != '-1')
  else:
    search_results = (d['title'] for d in raw_results['query']['geosearch'])

  return list(search_results)


@cache
def suggest(query):
  '''
  Get a Wikipedia search suggestion for `query`.
  Returns a string or None if no suggestion was found.
  '''

  search_params = {
    'list': 'search',
    'srinfo': 'suggestion',
    'srprop': '',
  }
  search_params['srsearch'] = query

  raw_result = _wiki_request(search_params)

  if raw_result['query'].get('searchinfo'):
    return raw_result['query']['searchinfo']['suggestion']

  return None


def random(pages=1):
  '''
  Get a list of random Wikipedia article titles.

  .. note:: Random only gets articles from namespace 0, meaning no Category, User talk, or other meta-Wikipedia pages.

  Keyword arguments:

  * pages - the number of random pages returned (max of 10)
  '''
  #http://en.wikipedia.org/w/api.php?action=query&list=random&rnlimit=5000&format=jsonfm
  query_params = {
    'list': 'random',
    'rnnamespace': 0,
    'rnlimit': pages,
  }

  request = _wiki_request(query_params)
  titles = [page['title'] for page in request['query']['random']]

  if len(titles) == 1:
    return titles[0]

  return titles


@cache
def summary(title, sentences=0, chars=0, auto_suggest=True, redirect=True):
  '''
  Plain text summary of the page.

  .. note:: This is a convenience wrapper - auto_suggest and redirect are enabled by default

  Keyword arguments:

  * sentences - if set, return the first `sentences` sentences (can be no greater than 10).
  * chars - if set, return only the first `chars` characters (actual text returned may be slightly longer).
  * auto_suggest - let Wikipedia find a valid page title for the query
  * redirect - allow redirection without raising RedirectError
  '''

  # use auto_suggest and redirect to get the correct article
  # also, use page's error checking to raise DisambiguationError if necessary
  page_info = page(title, auto_suggest=auto_suggest, redirect=redirect)
  title = page_info.title
  pageid = page_info.pageid

  query_params = {
    'prop': 'extracts',
    'explaintext': '',
    'titles': title
  }

  if sentences:
    query_params['exsentences'] = sentences
  elif chars:
    query_params['exchars'] = chars
  else:
    query_params['exintro'] = ''

  request = _wiki_request(query_params)
  summary = request['query']['pages'][pageid]['extract']

  return summary


def page(title=None, pageid=None, auto_suggest=True, redirect=True, preload=False):
  '''
  Get a WikipediaPage object for the page with title `title` or the pageid
  `pageid` (mutually exclusive).

  Keyword arguments:

  * title - the title of the page to load
  * pageid - the numeric pageid of the page to load
  * auto_suggest - let Wikipedia find a valid page title for the query
  * redirect - allow redirection without raising RedirectError
  * preload - load content, summary, images, references, and links during initialization
  '''

  if title is not None:
    if auto_suggest:
      results, suggestion = search(title, results=1, suggestion=True)
      try:
        title = suggestion or results[0]
      except IndexError:
        # if there is no suggestion or search results, the page doesn't exist
        raise PageError(title)
    return WikipediaPage(title, redirect=redirect, preload=preload)
  elif pageid is not None:
    return WikipediaPage(pageid=pageid, preload=preload)
  else:
    raise ValueError("Either a title or a pageid must be specified")


def languages():
    '''
    List all the currently supported language prefixes (usually ISO language code).

    Can be inputted to `set_lang` to change the Mediawiki that `wikipedia` requests
    results from.

    Returns: dict of <prefix>: <local_lang_name> pairs. To get just a list of prefixes,
    use `wikipedia.languages().keys()`.
    '''
    response = _wiki_request({
      'meta': 'siteinfo',
      'siprop': 'languages'
    })
    languages = response['query']['languages']
    return {
      lang['code']: lang['*']
      for lang in languages
    }


def donate():
  '''
  Open up the Wikimedia donate page in your favorite browser.
  '''
  import webbrowser
  webbrowser.open(Configuration().get_donate_url(), new=2)
