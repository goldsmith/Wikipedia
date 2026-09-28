"""Optional framework regression: pip install langchain-community==0.4.2."""
import pytest

pytest.importorskip('langchain_community')
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.utilities import WikipediaAPIWrapper
from tests.test_pages import record, MISSING
import wikipedia


def test_summary_wrapper(transport):
    transport.responses = [
        {'query': {'search': [{'title': 'Earth'}]}}, record(), record(extract='A planet.')]
    assert WikipediaAPIWrapper(top_k_results=1).run('Earth') == 'Page: Earth\nSummary: A planet.'
    assert len(transport.calls) == 3


def test_loader_full_metadata(transport):
    transport.responses = [
        {'query': {'search': [{'title': 'Earth'}]}}, record(), record(extract='A planet.'),
        record(categories=[{'title': 'Category:Planets'}]), {'batchcomplete': ''},
        record(links=[{'title': 'Moon'}]),
        record(extract='Full article.', revisions=[{'revid': 12, 'parentid': 11}]),
        record(extlinks=[{'*': 'https://example.org/source'}]),
        {'parse': {'tocdata': {'sections': [{'line': 'History'}]}}},
    ]
    docs = WikipediaLoader(query='Earth', load_max_docs=1, load_all_available_meta=True).load()
    assert len(docs) == 1
    assert docs[0].page_content == 'Full article.'
    metadata = docs[0].metadata
    assert metadata['title'] == 'Earth' and metadata['summary'] == 'A planet.'
    assert metadata['source'] == 'https://en.wikipedia.org/wiki/Earth'
    assert metadata['parent_id'] == 11 and metadata['revision_id'] == 12
    assert metadata['related_titles'] == ['Moon'] and metadata['sections'] == ['History']
    assert metadata['categories'] == ['Planets'] and metadata['image_urls'] == []
    assert metadata['references'] == ['https://example.org/source']
    assert not transport.responses


def test_missing_results_are_skipped(transport):
    transport.responses = [{'query': {'search': [{'title': 'Missing'}]}}, MISSING]
    assert WikipediaAPIWrapper(top_k_results=1).load('Missing') == []


def test_transport_error_remains_observable(transport):
    transport.responses = [{'error': {'code': 'badvalue', 'info': 'bad request'}}]
    with pytest.raises(wikipedia.RequestError):
        WikipediaAPIWrapper().run('Earth')
