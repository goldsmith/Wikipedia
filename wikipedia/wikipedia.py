import requests
from bs4 import BeautifulSoup

from .exceptions import *
from .util import cache

api_url = 'http://en.wikipedia.org/w/api.php'

def set_lang(prefix):
    '''
    Change the language of the API being requested. 
    Set `prefix` to one of the two letter prefixes found on the `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.

    After setting the language, the cache for ``search``, ``suggest``, and ``summary`` will be cleared.

    .. note:: Make sure you search for page titles in the language that you have set.
    '''
    global api_url
    api_url = 'http://' + prefix.lower() + '.wikipedia.org/w/api.php'

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
        'srlimit': results
    }
    if suggestion:
        search_params['srinfo'] = 'suggestion'
    search_params['srsearch'] = query
    search_params['limit'] = results

    raw_results = _wiki_request(**search_params)
    search_results = (d['title'] for d in raw_results['query']['search'])

    if suggestion:
        if raw_results['query'].get('searchinfo'):
            return list(search_results), raw_results['query']['searchinfo']['suggestion']
        else:
            return list(search_results), None

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

    raw_result = _wiki_request(**search_params)

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

    request = _wiki_request(**query_params)
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

    * sentences - if set, return the first `sentences` sentences
    * chars - if set, return only the first `chars` characters.
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

    request = _wiki_request(**query_params)
    summary = request['query']['pages'][pageid]['extract']

    return summary


def page(title, auto_suggest=True, redirect=True, preload=False):
    '''
    Get a WikipediaPage object for the page with title `title`.

    Keyword arguments:

    * auto_suggest - let Wikipedia find a valid page title for the query
    * redirect - allow redirection without raising RedirectError
    * preload - load content, summary, images, references, and links during initialization
    '''

    if auto_suggest:
        results, suggestion = search(title, results=1, suggestion=True)
        try:
            title = suggestion or results[0]
        except IndexError:
            # if there is no suggestion or search results, the page doesn't exist
            raise PageError(title)

    return WikipediaPage(title, redirect=redirect, preload=preload)


class WikipediaPage(object):
    '''
    Contains data from a Wikipedia page.
    Uses property methods to filter data from the raw HTML.
    '''

    def __init__(self, title, redirect=True, preload=False, original_title=''):
        self.title = title
        self.original_title = original_title or title

        self.load(redirect=redirect, preload=preload)

        if preload:
            for prop in ['content', 'summary', 'images', 'references', 'links']:
                getattr(self, prop)

    def __repr__(self):
        return u'<WikipediaPage \'%s\'>' % self.title

    def load(self, redirect=True, preload=False):
        '''
        Load basic information from Wikipedia.
        Confirm that page exists and is not a disambiguation/redirect.
        '''

        query_params = {
            'prop': 'info|pageprops',
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'titles': self.title
        }

        request = _wiki_request(**query_params)
        pageid = request['query']['pages'].keys()[0]
        data = request['query']['pages'][pageid]

        # missing is equal to empty string if it is True
        if data.get('missing') == '':
            raise PageError(self.title)

        # same thing for redirect
        elif data.get('redirect') == '':
            if redirect:
                # change the title and reload the whole object
                query_params = {
                    'prop': 'extracts',
                    'explaintext': '',
                    'titles': self.title
                }

                request = _wiki_request(**query_params)
                title = ' '.join(request['query']['pages'][pageid]['extract'].split()[1:])

                self.__init__(title, redirect=redirect, preload=preload)

            else:
                raise RedirectError(self.title)

        # since we only asked for disambiguation in ppprop,
        # if a pageprop is returned,
        # then the page must be a disambiguation page
        elif data.get('pageprops'):
            request = _wiki_request(titles=self.title, prop='revisions', rvprop='content', rvparse='', rvlimit=1)
            html = request['query']['pages'][pageid]['revisions'][0]['*']

            lis = BeautifulSoup(html).find_all('li')
            filtered_lis = [li for li in lis if not 'tocsection' in ''.join(li.get('class', []))]
            may_refer_to = [li.a.get_text() for li in filtered_lis]

            raise DisambiguationError(self.title, may_refer_to)

        else:
            self.pageid = pageid
            self.url = data['fullurl']

    def html(self):
        '''
        Get full page HTML.

        .. warning:: this can get pretty slow on long pages.
        '''

        if not getattr(self, '_html', False):
            query_params = {
                'prop': 'revisions',
                'rvprop': 'content',
                'rvlimit': 1,
                'rvparse': '',
                'titles': self.title
            }

            request = _wiki_request(**query_params)
            self._html = request['query']['pages'][self.pageid]['revisions'][0]['*']

        return self._html

    @property
    def content(self):
        '''
        Plain text content of the page, excluding images, tables, and other data.
        '''

        if not getattr(self, '_content', False):
            query_params = {
                'prop': 'extracts',
                'explaintext': '',
                'titles': self.title
            }

            request = _wiki_request(**query_params)
            self._content = request['query']['pages'][self.pageid]['extract']

        return self._content

    @property
    def summary(self):
        '''
        Plain text summary of the page.

        Keyword arguments:

        * sentences - if set, return the first `sentences` sentences
        * chars - if set, return only the first `chars` characters.
        '''

        # cache the most common form of invoking summary
        if not getattr(self, '_summary', False):
            query_params = {
                'prop': 'extracts',
                'explaintext': '',
                'exintro': '',
                'titles': self.title
            }

            request = _wiki_request(**query_params)
            self._summary = request['query']['pages'][self.pageid]['extract']

        return self._summary

    @property
    def images(self):
        '''
        List of URLs of images on the page.
        '''

        if not getattr(self, '_images', False):
            query_params = {
                'generator': 'images',
                'gimlimit': 'max',
                'prop': 'imageinfo',
                'iiprop': 'url',
                'titles': self.title,
            }

            request = _wiki_request(**query_params)

            image_keys = request['query']['pages'].keys()
            images = (request['query']['pages'][key] for key in image_keys)
            self._images = [image['imageinfo'][0]['url'] for image in images if image.get('imageinfo')]

        return self._images

    @property
    def references(self):
        '''
        List of URLs of external links on a page.
        May include external links within page that aren't technically cited anywhere.
        '''

        if not getattr(self, '_references', False):
            query_params = {
                'prop': 'extlinks',
                'ellimit': 'max',
                'titles': self.title,
            }

            request = _wiki_request(**query_params)

            links = request['query']['pages'][self.pageid]['extlinks']
            relative_urls = (link['*'] for link in links)

            def add_protocol(url):
                return url if url.startswith('http') else 'http:' + url

            self._references = [add_protocol(url) for url in relative_urls]

        return self._references

    @property
    def links(self):
        '''
        List of titles of Wikipedia page links on a page.

        .. note:: Only includes articles from namespace 0, meaning no Category, User talk, or other meta-Wikipedia pages.
        '''

        if not getattr(self, '_links', False):
            self._links = []

            request = {
                'prop': 'links',
                'plnamespace': 0,
                'pllimit': 'max',
                'titles': self.title,
            }
            lastContinue = {}

            # based on https://www.mediawiki.org/wiki/API:Query#Continuing_queries
            while True:
                params = request.copy()
                params.update(lastContinue)
                
                request = _wiki_request(**params)
                self._links.extend([link['title'] for link in request['query']['pages'][self.pageid]['links']])

                if 'continue' not in request:
                    break

                lastContinue = request['continue']

        return self._links


def donate():
    '''
    Open up the Wikimedia donate page in your favorite browser.
    '''
    import webbrowser
    webbrowser.open('https://donate.wikimedia.org/w/index.php?title=Special:FundraiserLandingPage', new=2)


def _wiki_request(**params):
    '''
    Make a request to the Wikipedia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''
    params['format'] = 'json'
    params['action'] = 'query'

    headers = {
        'User-Agent': 'wikipedia (https://github.com/goldsmith/Wikipedia/)'
    }

    r = requests.get(api_url, params=params, headers=headers)

    return r.json()
