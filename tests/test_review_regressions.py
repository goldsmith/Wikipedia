"""Edge cases found during final review of response and Unicode handling."""
import io
import sys
import pytest
import wikipedia
from wikipedia import wikipedia as wiki
from tests.conftest import Response
from tests.test_pages import record, load, MISSING


@pytest.mark.parametrize('pageid', [42, 0])
def test_missing_id_keeps_id_attribute(transport, pageid):
    transport.responses = [MISSING]
    with pytest.raises(wikipedia.PageError) as exc:
        wiki.page(pageid=pageid)
    assert exc.value.pageid == pageid


def test_null_toc_is_empty_and_cached(transport):
    # Observed from the live parse API on 2026-09-28 for heading-free wikitext.
    p = load(transport)
    transport.responses = [{'parse': {'tocdata': None}}]
    assert p.sections == []
    assert p.sections == []
    assert len(transport.calls) == 2


def test_malformed_pageprops_is_typed(transport):
    transport.responses = [record(pageprops=None)]
    with pytest.raises(wikipedia.RequestError):
        wiki.page('Earth', auto_suggest=False)


def test_empty_invalid_searchinfo_is_typed(transport):
    transport.responses = [{'query': {'search': [], 'searchinfo': []}}]
    with pytest.raises(wikipedia.RequestError):
        wiki.search('Earth', suggestion=True)


def test_unicode_repr_does_not_encode_to_terminal(transport, monkeypatch):
    p = load(transport, title='地球')
    stdout = io.TextIOWrapper(io.BytesIO(), encoding='ascii')
    monkeypatch.setattr(sys, 'stdout', stdout)
    assert repr(p) == "<WikipediaPage '地球'>"


@pytest.mark.parametrize('header', ['invalid', 'NaN', '-1'])
def test_invalid_retry_after_uses_safe_default(transport, header):
    transport.responses = [Response(status=429, headers={'Retry-After': header}), {'query': {}}]
    wiki._wiki_request({})
    assert transport.sleeps == [5]


def test_non_transient_requests_error_is_typed(transport):
    transport.responses = [wiki.requests.TooManyRedirects('loop')]
    with pytest.raises(wikipedia.RequestError):
        wiki._wiki_request({})
    assert len(transport.calls) == 1
