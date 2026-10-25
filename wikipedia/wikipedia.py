from __future__ import unicode_literals

import requests
import time
import atexit
import math
from email.utils import parsedate_to_datetime
from numbers import Real
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from decimal import Decimal

from .exceptions import (
  PageError, DisambiguationError, RedirectError, HTTPTimeoutError,
  WikipediaException, RequestError, ODD_ERROR_MESSAGE)
from .util import cache, stdout_encode, debug
import re

API_URL = 'https://en.wikipedia.org/w/api.php'
RATE_LIMIT = False
RATE_LIMIT_MIN_WAIT = None
RATE_LIMIT_LAST_CALL = None
USER_AGENT = 'wikipedia (https://github.com/goldsmith/Wikipedia/)'
TIMEOUT = (5, 15)
_SESSION = requests.Session()
atexit.register(_SESSION.close)


def set_timeout(timeout):
  """Set connect/read timeout seconds, a (connect, read) pair, or None.

  The default is (5, 15). None explicitly disables timeouts. A read timeout
  limits inactivity while reading, not the total wall time of an operation.
  """
  values = timeout if isinstance(timeout, tuple) else (timeout,)
  if timeout is not None and (
      len(values) not in (1, 2) or
      (isinstance(timeout, tuple) and len(values) != 2) or
      any(isinstance(v, bool) or not isinstance(v, Real) or
          not math.isfinite(v) or v <= 0 for v in values)):
    raise ValueError('timeout must be positive seconds, a positive pair, or None')
  global TIMEOUT
  TIMEOUT = timeout


def set_lang(prefix):
  '''
  Change the language of the API being requested.
  Set `prefix` to one of the two letter prefixes found on the `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.

  After setting the language, all module function caches will be cleared.
  Existing page objects retain their original language.

  .. note:: Make sure you search for page titles in the language that you have set.
  '''
  global API_URL
  API_URL = 'https://' + prefix.lower() + '.wikipedia.org/w/api.php'

  for cached_func in (search, suggest, summary, geosearch, languages):
    cached_func.clear_cache()


def set_user_agent(user_agent_string):
  '''
  Set the User-Agent string to be used for all requests.

  Arguments:

  * user_agent_string - (string) a string specifying the User-Agent header
  '''
  global USER_AGENT
  USER_AGENT = user_agent_string


def set_rate_limiting(rate_limit, min_wait=timedelta(milliseconds=50)):
  '''
  Enable or disable rate limiting on requests to the Mediawiki servers.
  If rate limiting is not enabled, under some circumstances (depending on
  load on Wikipedia, the number of requests you and other `wikipedia` users
  are making, and other factors), Wikipedia may return an HTTP timeout error.

  Enabling rate limiting generally prevents that issue, but please note that
  HTTPTimeoutError still might be raised.

  Arguments:

  * rate_limit - (Boolean) whether to enable rate limiting or not

  Keyword arguments:

  * min_wait - if rate limiting is enabled, `min_wait` is a timedelta describing the minimum time to wait before requests.
         Defaults to timedelta(milliseconds=50)
  '''
  global RATE_LIMIT
  global RATE_LIMIT_MIN_WAIT
  global RATE_LIMIT_LAST_CALL

  RATE_LIMIT = rate_limit
  if not rate_limit:
    RATE_LIMIT_MIN_WAIT = None
  else:
    RATE_LIMIT_MIN_WAIT = min_wait

  RATE_LIMIT_LAST_CALL = None


@cache
def search(query, results=10, suggestion=False):
  '''
  Do a Wikipedia search for `query`.

  Keyword arguments:

  * results - the maximum number of results returned
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
      raise WikipediaException(raw_results['error']['info'])

  search_results = (_required(d, 'title', str) for d in
                    _required(_required(raw_results, 'query', dict), 'search', list))

  if suggestion:
    return list(search_results), _search_suggestion(raw_results)

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
      raise WikipediaException(raw_results['error']['info'])

  query_data = _required(raw_results, 'query', dict)
  search_pages = query_data.get('pages', None)
  if search_pages:
    search_pages = _required(query_data, 'pages', dict)
    search_results = (_required(v, 'title', str) for k, v in search_pages.items() if k != '-1')
  else:
    search_results = (_required(d, 'title', str) for d in _required(query_data, 'geosearch', list))

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

  return _search_suggestion(raw_result)


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
  titles = [_required(page, 'title', str) for page in
            _required(_required(request, 'query', dict), 'random', list)]

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
  * auto_suggest - try a search suggestion only if the exact title is missing
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

  request = page_info._request(query_params)
  summary = _required(_page_data(request, pageid), 'extract', str)

  return summary


def page(title=None, pageid=None, auto_suggest=True, redirect=True, preload=False):
  '''
  Get a WikipediaPage object for the page with title `title` or the pageid
  `pageid` (mutually exclusive).

  Keyword arguments:

  * title - the title of the page to load
  * pageid - the numeric pageid of the page to load
  * auto_suggest - try a search suggestion only if the exact title is missing
  * redirect - allow redirection without raising RedirectError
  * preload - load content, summary, images, references, and links during initialization
  '''

  if title is not None:
    try:
      return WikipediaPage(title, redirect=redirect, preload=preload)
    except PageError:
      if not auto_suggest:
        raise
      results, suggestion = search(title, results=1, suggestion=True)
      candidate = suggestion or (results[0] if results else None)
      if not candidate or candidate == title:
        raise PageError(None, title) from None
      return WikipediaPage(candidate, redirect=redirect, preload=preload,
                           original_title=title)
  elif pageid is not None:
    return WikipediaPage(pageid=pageid, redirect=redirect, preload=preload)
  else:
    raise ValueError("Either a title or a pageid must be specified")



class WikipediaPage(object):
  '''
  Contains data from a Wikipedia page.
  Uses property methods to filter data from the raw HTML.
  '''

  def __init__(self, title=None, pageid=None, redirect=True, preload=False, original_title=''):
    self._api_url = API_URL
    if title is not None:
      self.title = title
      self.original_title = original_title or title
    elif pageid is not None:
      self.pageid = pageid
    else:
      raise ValueError("Either a title or a pageid must be specified")

    self.__load(redirect=redirect, preload=preload)

    if preload:
      for prop in ('content', 'summary', 'images', 'references', 'links', 'sections'):
        getattr(self, prop)

  def __repr__(self):
    return stdout_encode(u'<WikipediaPage \'{}\'>'.format(self.title))

  def _request(self, params):
    return _wiki_request(params, api_url=self._api_url)

  def __eq__(self, other):
    try:
      return (
        self.pageid == other.pageid
        and self.title == other.title
        and self.url == other.url
      )
    except Exception:
      return False

  def __load(self, redirect=True, preload=False):
    '''
    Load basic information from Wikipedia.
    Confirm that page exists and is not a disambiguation/redirect.

    Does not need to be called manually, should be called automatically during __init__.
    '''
    query_params = {
      'prop': 'info|pageprops',
      'inprop': 'url',
      'ppprop': 'disambiguation',
      'redirects': '',
    }
    if not hasattr(self, 'pageid'):
      query_params['titles'] = self.title
    else:
      query_params['pageids'] = self.pageid

    request = self._request(query_params)

    query = request['query']
    data = _page_data(request)
    if 'missing' in data or 'invalid' in data:
      if hasattr(self, 'title'):
        raise PageError(None, self.title)
      raise PageError(pageid=self.pageid)
    if query.get('redirects') and not redirect:
      raise RedirectError(getattr(self, 'title', data.get('title', '')))
    self.pageid = str(_required(data, 'pageid', int))
    self.title = _required(data, 'title', str)
    self.url = _required(data, 'fullurl', str)
    pageprops = data.get('pageprops', {})
    if not isinstance(pageprops, dict):
      raise RequestError('Wikipedia returned malformed pageprops')
    if 'disambiguation' in pageprops:
      parsed = _required(self._request({'action': 'parse', 'prop': 'text|links',
                                       'page': self.title}), 'parse', dict)
      self._html = _required(_required(parsed, 'text', dict), '*', str)
      allowed = {_required(link, '*', str) for link in _required(parsed, 'links', list)
                 if _required(link, 'ns', int) == 0 and 'exists' in link}
      soup = BeautifulSoup(self._html, 'html.parser')
      options = []
      for li in soup.find_all('li'):
        if any('tocsection' in name for name in li.get('class', [])):
          continue
        for link in li.find_all('a', href=True):
          target = urlsplit(link['href'])
          if target.netloc and target.netloc != urlsplit(self._api_url).netloc:
            continue
          if not target.path.startswith('/wiki/') or 'new' in link.get('class', []):
            continue
          title = unquote(target.path[len('/wiki/'):]).replace('_', ' ')
          if title not in allowed:
            continue
          if title not in options:
            options.append(title)
          break
      raise DisambiguationError(self.title, options)

  def __continued_query(self, query_params):
    '''
    Based on https://www.mediawiki.org/wiki/API:Query#Continuing_queries
    '''
    query_params = dict(query_params, **self.__title_query_param)
    last_continue = {}
    seen = set()
    prop = query_params.get('prop')
    while True:
      request = self._request(dict(query_params, **last_continue))
      if 'generator' in query_params:
        if 'query' not in request and 'batchcomplete' in request:
          pages = {}
        else:
          pages = _required(_required(request, 'query', dict), 'pages', dict)
        for datum in pages.values():
          if not isinstance(datum, dict):
            raise RequestError('Wikipedia returned a malformed generated page')
          yield datum
      else:
        data = _page_data(request, self.pageid)
        if 'missing' in data:
          raise PageError(pageid=self.pageid)
        values = data.get(prop, [])
        if not isinstance(values, list) or any(not isinstance(v, dict) for v in values):
          raise RequestError('Wikipedia returned a malformed {} property'.format(prop))
        yield from values
      if 'continue' not in request:
        break
      last_continue = _required(request, 'continue', dict)
      token = repr(sorted(last_continue.items()))
      if not last_continue or token in seen:
        raise RequestError('Wikipedia repeated or omitted a continuation token')
      seen.add(token)

  @property
  def __title_query_param(self):
    if getattr(self, 'title', None) is not None:
      return {'titles': self.title}
    else:
      return {'pageids': self.pageid}

  def html(self):
    '''
    Get full page HTML.

    .. warning:: This can get pretty slow on long pages.
    '''

    if not hasattr(self, '_html'):
      request = self._request({'action': 'parse', 'prop': 'text', 'page': self.title})
      text = _required(_required(request, 'parse', dict), 'text', dict)
      self._html = _required(text, '*', str)

    return self._html

  @property
  def content(self):
    '''
    Plain text content of the page, excluding images, tables, and other data.
    '''

    if not hasattr(self, '_content'):
      query_params = {
        'prop': 'extracts|revisions',
        'explaintext': '',
        'rvprop': 'ids'
      }
      if not getattr(self, 'title', None) is None:
         query_params['titles'] = self.title
      else:
         query_params['pageids'] = self.pageid
      request = self._request(query_params)
      data = _page_data(request, self.pageid)
      content = _required(data, 'extract', str)
      revisions = _required(data, 'revisions', list)
      if not revisions or not isinstance(revisions[0], dict):
        raise RequestError('Wikipedia returned no revision metadata')
      revision_id = _required(revisions[0], 'revid', int)
      parent_id = _required(revisions[0], 'parentid', int)
      self._content = content
      self._revision_id = revision_id
      self._parent_id = parent_id

    return self._content

  @property
  def revision_id(self):
    '''
    Revision ID of the page.

    The revision ID is a number that uniquely identifies the current
    version of the page. It can be used to create the permalink or for
    other direct API calls. See `Help:Page history
    <http://en.wikipedia.org/wiki/Wikipedia:Revision>`_ for more
    information.
    '''

    if not hasattr(self, '_revision_id'):
      # fetch the content (side effect is loading the revid)
      self.content

    return self._revision_id

  @property
  def parent_id(self):
    '''
    Revision ID of the parent version of the current revision of this
    page. See ``revision_id`` for more information.
    '''

    if not hasattr(self, '_parent_id'):
      # fetch the content (side effect is loading the revid)
      self.content

    return self._parent_id

  @property
  def summary(self):
    '''
    Plain text summary of the page.
    '''

    if not hasattr(self, '_summary'):
      query_params = {
        'prop': 'extracts',
        'explaintext': '',
        'exintro': '',
      }
      if not getattr(self, 'title', None) is None:
         query_params['titles'] = self.title
      else:
         query_params['pageids'] = self.pageid

      request = self._request(query_params)
      self._summary = _required(_page_data(request, self.pageid), 'extract', str)

    return self._summary

  @property
  def images(self):
    '''
    List of URLs of images on the page.
    '''

    if not hasattr(self, '_images'):
      images = []
      for page in self.__continued_query({
          'generator': 'images',
          'gimlimit': 'max',
          'prop': 'imageinfo',
          'iiprop': 'url',
        }):
        info = page.get('imageinfo', [])
        if not isinstance(info, list):
          raise RequestError('Wikipedia returned malformed image metadata')
        if not info:
          continue
        if not isinstance(info[0], dict):
          raise RequestError('Wikipedia returned malformed image metadata')
        if 'url' in info[0]:
          images.append(_required(info[0], 'url', str))
      self._images = images

    return list(self._images)

  @property
  def coordinates(self):
    '''
    Tuple of Decimals in the form of (lat, lon) or None
    '''
    if not hasattr(self, '_coordinates'):
      query_params = {
        'prop': 'coordinates',
        'colimit': 'max',
        'titles': self.title,
      }

      request = self._request(query_params)

      coordinates = _page_data(request, self.pageid).get('coordinates', [])
      if not isinstance(coordinates, list):
        raise RequestError('Wikipedia returned malformed coordinates')
      if coordinates:
        try:
          self._coordinates = (Decimal(str(coordinates[0]['lat'])), Decimal(str(coordinates[0]['lon'])))
        except (KeyError, TypeError, ArithmeticError) as exc:
          raise RequestError('Wikipedia returned malformed coordinates') from exc
      else:
        self._coordinates = None

    return self._coordinates

  @property
  def references(self):
    '''
    List of URLs of external links on a page.
    May include external links within page that aren't technically cited anywhere.
    '''

    if not hasattr(self, '_references'):
      def add_protocol(url):
        return 'https:' + url if url.startswith('//') else url

      self._references = [
        add_protocol(_required(link, '*', str))
        for link in self.__continued_query({
          'prop': 'extlinks',
          'ellimit': 'max'
        })
      ]

    return list(self._references)

  @property
  def links(self):
    '''
    List of titles of Wikipedia page links on a page.

    .. note:: Only includes articles from namespace 0, meaning no Category, User talk, or other meta-Wikipedia pages.
    '''

    if not hasattr(self, '_links'):
      self._links = [
        _required(link, 'title', str)
        for link in self.__continued_query({
          'prop': 'links',
          'plnamespace': 0,
          'pllimit': 'max'
        })
      ]

    return list(self._links)

  @property
  def categories(self):
    '''
    List of categories of a page.
    '''

    if not hasattr(self, '_categories'):
      self._categories = [x.split(':', 1)[-1] for x in
        [_required(link, 'title', str)
        for link in self.__continued_query({
          'prop': 'categories',
          'cllimit': 'max'
        })
      ]]

    return list(self._categories)

  @property
  def sections(self):
    '''
    List of section titles from the table of contents on the page.
    '''

    if not hasattr(self, '_sections'):
      request = self._request({'action': 'parse', 'prop': 'tocdata', 'page': self.title})
      parsed = _required(request, 'parse', dict)
      # MediaWiki returns explicit null for a page without a table of contents.
      if 'tocdata' in parsed and parsed['tocdata'] is None:
        sections = []
      else:
        sections = _required(_required(parsed, 'tocdata', dict), 'sections', list)
      self._sections = [BeautifulSoup(_required(section, 'line', str), 'html.parser').get_text()
                        for section in sections]

    return list(self._sections)

  def section(self, section_title):
    '''
    Get the plain text content of a section from `self.sections`.
    Returns None if `section_title` isn't found, otherwise returns a whitespace stripped string.

    This is a convenience method that wraps self.content.

    .. warning:: Calling `section` on a section that has subheadings will NOT return
           the full text of all of the subsections. It only gets the text between
           `section_title` and the next subheading, which is often empty.
    '''

    headings = list(re.finditer(r'^(={2,6})[ \t]*(.*?)[ \t]*\1[ \t]*$', self.content, re.MULTILINE))
    for index, heading in enumerate(headings):
      if heading.group(2).strip() == section_title:
        end = headings[index + 1].start() if index + 1 < len(headings) else len(self.content)
        return self.content[heading.end():end].strip()
    return None


@cache
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

  languages = _required(_required(response, 'query', dict), 'languages', list)

  return {
    _required(lang, 'code', str): _required(lang, '*', str)
    for lang in languages
  }


def donate():
  '''
  Open up the Wikimedia donate page in your favorite browser.
  '''
  import webbrowser

  webbrowser.open('https://donate.wikimedia.org/w/index.php?title=Special:FundraiserLandingPage', new=2)


def _search_suggestion(response):
  info = _required(response, 'query', dict).get('searchinfo', {})
  if not isinstance(info, dict):
    raise RequestError('Wikipedia returned malformed search information')
  suggestion = info.get('suggestion')
  if suggestion is not None and not isinstance(suggestion, str):
    raise RequestError('Wikipedia returned a malformed suggestion')
  return suggestion


def _required(mapping, key, expected_type):
  if not isinstance(mapping, dict) or not isinstance(mapping.get(key), expected_type):
    raise RequestError('Wikipedia returned a missing or malformed {}'.format(key))
  return mapping[key]


def _page_data(response, pageid=None):
  pages = _required(_required(response, 'query', dict), 'pages', dict)
  if not pages:
    raise RequestError('Wikipedia returned no page records')
  if pageid is None:
    if len(pages) != 1:
      raise RequestError('Wikipedia returned ambiguous page records')
    data = next(iter(pages.values()))
  else:
    data = pages.get(str(pageid))
  if not isinstance(data, dict):
    raise RequestError('Wikipedia returned a missing or malformed page record')
  return data


def _retry_after(value):
  """Parse HTTP delta-seconds or a date; ignore invalid header values."""
  if value is None:
    return None
  try:
    seconds = float(value)
  except (TypeError, ValueError):
    try:
      seconds = parsedate_to_datetime(value).timestamp() - time.time()
    except (TypeError, ValueError, OverflowError):
      return None
  else:
    if seconds < 0:
      return None
  return max(0.0, seconds) if math.isfinite(seconds) else None


def _wiki_request(params, api_url=None):
  '''
  Make a request to the Wikipedia API using the given search parameters.
  Returns a parsed dict of the JSON response.
  '''
  global RATE_LIMIT_LAST_CALL
  params = dict(params, format='json')
  params.setdefault('action', 'query')
  query = next((params[k] for k in ('titles', 'pageids', 'srsearch', 'gscoord')
                if k in params), params)
  slept = 0.0
  for attempt in range(3):
    if RATE_LIMIT and RATE_LIMIT_LAST_CALL is not None:
      wait = RATE_LIMIT_MIN_WAIT.total_seconds() - (time.monotonic() - RATE_LIMIT_LAST_CALL)
      if wait > 0:
        time.sleep(wait)
    retry_after = None
    throttled = False
    try:
      response = _SESSION.get(api_url or API_URL, params=params,
                              headers={'User-Agent': USER_AGENT}, timeout=TIMEOUT)
    except requests.Timeout as exc:
      failure = HTTPTimeoutError(query)
      failure.__cause__ = exc
      retryable = True
    except requests.ConnectionError as exc:
      failure = RequestError('Connection to Wikipedia failed: {}'.format(exc))
      failure.__cause__ = exc
      retryable = True
    except requests.RequestException as exc:
      raise RequestError('Wikipedia request failed: {}'.format(exc)) from exc
    else:
      status = response.status_code
      retry_after = _retry_after(response.headers.get('Retry-After'))
      try:
        data = response.json()
      except ValueError as exc:
        if 200 <= status < 300:
          raise RequestError('Wikipedia returned invalid JSON', status_code=status) from exc
        data = {}
      error = data.get('error', {}) if isinstance(data, dict) else {}
      if not isinstance(error, dict):
        raise RequestError('Wikipedia returned a malformed API error', status_code=status)
      code = error.get('code')
      message = error.get('info', code or 'HTTP {}'.format(status))
      if not 200 <= status < 300 or error:
        retryable = status in (429, 502, 503, 504) or code in ('maxlag', 'ratelimited')
        throttled = status == 429 or code in ('maxlag', 'ratelimited')
        if message in ('HTTP request timed out.', 'Pool queue is full'):
          failure = HTTPTimeoutError(query)
          retryable = True
        else:
          failure = RequestError(message, status_code=status, api_code=code,
                                 retry_after=retry_after)
      else:
        action = params['action']
        if not isinstance(data, dict) or not isinstance(data.get(action), dict):
          # Empty image generators legitimately omit query while returning batchcomplete.
          if not (action == 'query' and 'generator' in params and
                  isinstance(data, dict) and 'batchcomplete' in data):
            raise RequestError('Wikipedia returned a malformed {} response'.format(action),
                               status_code=status)
        return data
    finally:
      if RATE_LIMIT:
        RATE_LIMIT_LAST_CALL = time.monotonic()

    if not retryable or attempt == 2:
      raise failure
    delay = retry_after if retry_after is not None else (5 if throttled else 1) * 2 ** attempt
    if slept + delay > 30:
      raise failure
    time.sleep(delay)
    slept += delay
