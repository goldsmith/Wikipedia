from .exceptions import (
  DisambiguationError, PageError, RedirectError, ODD_ERROR_MESSAGE
)
from decimal import Decimal
from bs4 import BeautifulSoup
from .config import Configuration
from .language import Language
from .util import stdout_encode
import re


class WikipediaPage(object):
  '''
  Contains data from a Wikipedia page.
  Uses property methods to filter data from the raw HTML.
  '''
  def __init__(self, title=None, pageid=None, redirect=True, preload=False, original_title=''):
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

  def __eq__(self, other):
    try:
      return (
        self.pageid == other.pageid
        and self.title == other.title
        and self.url == other.url
      )
    except:
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
    if not getattr(self, 'pageid', None):
      query_params['titles'] = self.title
    else:
      query_params['pageids'] = self.pageid

    request = _wiki_request(query_params)
   
    query = request['query']
    pageid = list(query['pages'].keys())[0]
    page = query['pages'][pageid]

    # missing is present if the page is missing
    if 'missing' in page:
      if hasattr(self, 'title'):
        raise PageError(self.title)
      else:
        raise PageError(pageid=self.pageid)

    # same thing for redirect, except it shows up in query instead of page for
    # whatever silly reason
    elif 'redirects' in query:
      if redirect:
        redirects = query['redirects'][0]
        if 'normalized' in query:
          normalized = query['normalized'][0]
          assert normalized['from'] == self.title, ODD_ERROR_MESSAGE
          from_title = normalized['to']

        else:
          from_title = self.title

        assert redirects['from'] == from_title, ODD_ERROR_MESSAGE

        # change the title and reload the whole object
        self.__init__(redirects['to'], redirect=redirect, preload=preload)

      else:
        raise RedirectError(getattr(self, 'title', page['title']))

    # since we only asked for disambiguation in ppprop,
    # if a pageprop is returned,
    # then the page must be a disambiguation page
    elif 'pageprops' in page:
      query_params = {
        'prop': 'revisions',
        'rvprop': 'content',
        'rvparse': '',
        'rvlimit': 1
      }
      if hasattr(self, 'pageid'):
        query_params['pageids'] = self.pageid
      else:
        query_params['titles'] = self.title
      request = _wiki_request(query_params)
      html = request['query']['pages'][pageid]['revisions'][0]['*']

      lis = BeautifulSoup(html, 'html.parser').find_all('li')
      filtered_lis = [li for li in lis if not 'tocsection' in ''.join(li.get('class', []))]
      may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]

      raise DisambiguationError(getattr(self, 'title', page['title']), may_refer_to)

    else:
      self.pageid = pageid
      self.title = page['title']
      self.url = page['fullurl']
      self.language = page['pagelanguage']

  def __continued_query(self, query_params):
    '''
    Based on https://www.mediawiki.org/wiki/API:Query#Continuing_queries
    '''
    query_params.update(self.__title_query_param)

    last_continue = {}
    prop = query_params.get('prop', None)

    while True:
      params = query_params.copy()
      params.update(last_continue)

      request = _wiki_request(params)

      if 'query' not in request:
        break

      pages = request['query']['pages']
      if 'generator' in query_params:
        for datum in pages.values():  # in python 3.3+: "yield from pages.values()"
          yield datum
      else:
        for datum in pages[self.pageid][prop]:
          yield datum

      if 'continue' not in request:
        break

      last_continue = request['continue']

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
    if not getattr(self, '_html', False):
      query_params = {
        'prop': 'revisions',
        'rvprop': 'content',
        'rvlimit': 1,
        'rvparse': '',
        'titles': self.title
      }

      request = _wiki_request(query_params)
      self._html = request['query']['pages'][self.pageid]['revisions'][0]['*']

    return self._html

  @property
  def content(self):
    '''
    Plain text content of the page, excluding images, tables, and other data.
    '''
    if not getattr(self, '_content', False):
      query_params = {
        'prop': 'extracts|revisions',
        'explaintext': '',
        'rvprop': 'ids'
      }
      query_params.update(self.__title_query_param)
      request = _wiki_request(query_params)
      self._content     = request['query']['pages'][self.pageid]['extract']
      self._revision_id = request['query']['pages'][self.pageid]['revisions'][0]['revid']
      self._parent_id   = request['query']['pages'][self.pageid]['revisions'][0]['parentid']

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
    if not getattr(self, '_revid', False):
      # fetch the content (side effect is loading the revid)
      self.content

    return self._revision_id

  @property
  def parent_id(self):
    '''
    Revision ID of the parent version of the current revision of this
    page. See ``revision_id`` for more information.
    '''
    if not getattr(self, '_parentid', False):
      # fetch the content (side effect is loading the revid)
      self.content

    return self._parent_id

  @property
  def summary(self):
    '''
    Plain text summary of the page.
    '''
    if not getattr(self, '_summary', False):
      query_params = {
        'prop': 'extracts',
        'explaintext': '',
        'exintro': '',
      }
      query_params.update(self.__title_query_param)

      request = _wiki_request(query_params)
      self._summary = request['query']['pages'][self.pageid]['extract']

    return self._summary

  @property
  def images(self):
    '''
    List of URLs of images on the page.
    '''
    if not getattr(self, '_images', False):
      self._images = [
        page['imageinfo'][0]['url']
        for page in self.__continued_query({
          'generator': 'images',
          'gimlimit': 'max',
          'prop': 'imageinfo',
          'iiprop': 'url',
        })
        if 'imageinfo' in page
      ]

    return self._images

  @property
  def coordinates(self):
    '''
    Tuple of Decimals in the form of (lat, lon) or None
    '''
    if not getattr(self, '_coordinates', False):
      query_params = {
        'prop': 'coordinates',
        'colimit': 'max',
        'titles': self.title,
      }

      request = _wiki_request(query_params)

      if 'query' in request:
        coordinates = request['query']['pages'][self.pageid]['coordinates']
        self._coordinates = (Decimal(coordinates[0]['lat']), Decimal(coordinates[0]['lon']))
      else:
        self._coordinates = None

    return self._coordinates

  @property
  def references(self):
    '''
    List of URLs of external links on a page.
    May include external links within page that aren't technically cited anywhere.
    '''
    if not getattr(self, '_references', False):
      def add_protocol(url):
        return url if url.startswith('http') else 'http:' + url

      self._references = [
        add_protocol(link['*'])
        for link in self.__continued_query({
          'prop': 'extlinks',
          'ellimit': 'max'
        })
      ]

    return self._references

  @property
  def links(self):
    '''
    List of titles of Wikipedia page links on a page.

    .. note:: Only includes articles from namespace 0, meaning no Category, User talk, or other meta-Wikipedia pages.
    '''
    if not getattr(self, '_links', False):
      self._links = [
        link['title']
        for link in self.__continued_query({
          'prop': 'links',
          'plnamespace': 0,
          'pllimit': 'max'
        })
      ]

    return self._links

  @property
  def categories(self):
    '''
    List of categories of a page.
    '''
    if not getattr(self, '_categories', False):
      self._categories = [re.sub(r'^Category:', '', x) for x in
        [link['title']
        for link in self.__continued_query({
          'prop': 'categories',
          'cllimit': 'max'
        })
      ]]

    return self._categories

  @property
  def sections(self):
    '''
    List of section titles from the table of contents on the page.
    '''
    if not getattr(self, '_sections', False):
      query_params = {
        'action': 'parse',
        'prop': 'sections',
      }
      if getattr(self, 'title', None) is not None:
        query_params.update({'page': self.title})
      else:
        query_params.update({'pageid': self.pageid})

      request = _wiki_request(query_params)
      self._sections = [section['line'] for section in request['parse']['sections']]

    return self._sections

  def section(self, section_title):
    '''
    Get the plain text content of a section from `self.sections`.
    Returns None if `section_title` isn't found, otherwise returns a whitespace stripped string.

    This is a convenience method that wraps self.content.

    .. warning:: Calling `section` on a section that has subheadings will NOT return
           the full text of all of the subsections. It only gets the text between
           `section_title` and the next subheading, which is often empty.
    '''

    section = u"== {} ==".format(section_title)
    try:
      index = self.content.index(section) + len(section)
    except ValueError:
      return None

    try:
      next_index = self.content.index("==", index)
    except ValueError:
      next_index = len(self.content)

    return self.content[index:next_index].lstrip("=").strip()

  def lang_title(self, lang_code):
    '''
    Get the title in specified language code
    Returns None if lang code or title isn't found, otherwise returns a string with title.
    Raise LanguageException if language doesn't exists
    '''
    query_params = {
      'prop': 'langlinks',
      'llurl': True,
    }
    query_params.update({'lllang': Language(lang_code).get_lang()})
    query_params.update(self.__title_query_param)
    request = _wiki_request(query_params)
    pageid = list(request['query']['pages'])[0]
    try:
        title = request['query']['pages'][pageid]['langlinks'][0]['*']
    except Exception as e:
        title = None
    return title


def _wiki_request(params):
    '''
    Make a request to the Wikipedia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''
    params['format'] = 'json'
    if not 'action' in params:
      params['action'] = 'query'

    headers = {
      'User-Agent': Configuration().get_user_agent()
    }

    rate_limit = Configuration().get_rate_limit()
    rate_limit_last_call = Configuration().get_rate_limit_last_call()
    rate_limit_min_wait = Configuration().get_rate_limit_min_wait()
    if rate_limit and rate_limit_last_call and \
      rate_limit_last_call + rate_limit_min_wait > datetime.now():

      # it hasn't been long enough since the last API call
      # so wait until we're in the clear to make the request

      wait_time = (rate_limit_last_call + rate_limit_min_wait) - datetime.now()
      time.sleep(int(wait_time.total_seconds()))
    r = Configuration().get_session().get(Configuration().get_api_url(), params=params, headers=headers)

    if rate_limit:
      rate_limit_last_call = datetime.now()

    return r.json()
