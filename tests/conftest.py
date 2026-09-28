"""Isolated historical fixtures plus a transport fake for regression tests."""
from copy import deepcopy
import pytest
from wikipedia import wikipedia as wiki
from request_mock_data import mock_data


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch, request):
    def unexpected_network(*args, **kwargs):
        pytest.fail('Offline tests attempted an unexpected HTTP request')
    monkeypatch.setattr(wiki.requests.sessions.Session, 'request', unexpected_network)
    for name in ("API_URL", "USER_AGENT", "RATE_LIMIT", "RATE_LIMIT_MIN_WAIT",
                 "RATE_LIMIT_LAST_CALL", "TIMEOUT"):
        if hasattr(wiki, name):
            monkeypatch.setattr(wiki, name, getattr(wiki, name))
    wiki.set_lang("en")
    wiki.set_rate_limiting(False)
    for value in vars(wiki).values():
        if isinstance(value, wiki.cache):
            value.clear_cache()
    if request.module.__name__.split(".")[-1] in {
        "page_test", "search_test", "geosearch_test", "lang_test"
    }:
        def historical_request(params, **kwargs):
            # Preserve original article fixtures while adapting retired API envelopes.
            if params.get('prop') == 'info|pageprops' and params.get('titles') == 'butteryfly':
                return {'query': {'pages': {'-1': {'title': 'butteryfly', 'missing': ''}}}}
            if params.get('action') == 'parse' and params.get('prop') in ('text', 'text|links'):
                old = {'prop': 'revisions', 'rvprop': 'content', 'rvlimit': 1,
                       'rvparse': '', 'titles': params['page']}
                data = mock_data['_wiki_request calls'][tuple(sorted(old.items()))]
                page = next(iter(data['query']['pages'].values()))
                html = page['revisions'][0]['*']
                parsed = {'text': {'*': html}}
                if params['prop'] == 'text|links':
                    # All links in this historical disambiguation fixture are articles.
                    from bs4 import BeautifulSoup
                    from urllib.parse import unquote, urlsplit
                    parsed['links'] = [
                        {'ns': 0, 'exists': '', '*': unquote(urlsplit(a['href']).path[6:]).replace('_', ' ')}
                        for a in BeautifulSoup(html, 'html.parser').find_all('a', href=True)
                        if a['href'].startswith('/wiki/')]
                return {'parse': parsed}
            if params.get('prop') == 'tocdata':
                old = dict(params, prop='sections')
                data = mock_data['_wiki_request calls'][tuple(sorted(old.items()))]
                return {'parse': {'tocdata': {'sections': deepcopy(data['parse']['sections'])}}}
            data = deepcopy(mock_data["_wiki_request calls"][tuple(sorted(params.items()))])
            if params.get('prop') == 'categories':
                # Old fixtures stored stripped names, unlike the actual API wire format.
                for page in data['query']['pages'].values():
                    for category in page.get('categories', []):
                        category['title'] = 'Category:' + category['title']
            return data
        monkeypatch.setattr(wiki, "_wiki_request", historical_request)
    yield
    for value in vars(wiki).values():
        if isinstance(value, wiki.cache):
            value.clear_cache()


class Response:
    def __init__(self, data=None, status=200, headers=None):
        self.data = {} if data is None else data
        self.status_code = status
        self.headers = headers or {}

    def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return deepcopy(self.data)


@pytest.fixture
def transport(monkeypatch):
    """Patch only the HTTP boundary, never the package request/parser code."""
    class Transport:
        def __init__(self):
            self.responses = []
            self.calls = []
            self.sleeps = []

        def get(self, url, **kwargs):
            self.calls.append((url, deepcopy(kwargs)))
            if not self.responses:
                raise AssertionError("Unexpected HTTP call: %r" % self.calls[-1])
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
            return response if isinstance(response, Response) else Response(response)

    fake = Transport()
    monkeypatch.setattr(wiki.requests, "get", fake.get)
    monkeypatch.setattr(wiki.requests.Session, "get", lambda self, *a, **k: fake.get(*a, **k))
    monkeypatch.setattr(wiki.time, "sleep", fake.sleeps.append)
    return fake
