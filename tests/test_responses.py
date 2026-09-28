import pytest
import wikipedia
from wikipedia import wikipedia as wiki
from tests.test_pages import load, record


@pytest.mark.parametrize("call,data", [
    (lambda: wiki.search('Earth'), {'query': {}}),
    (lambda: wiki.search('Earth'), {'query': {'search': [{'invalid': 'title'}]}}),
    (lambda: wiki.suggest('Earth'), {'query': {'searchinfo': {'totalhits': 4}}}),
    (lambda: wiki.geosearch(1, 2), {'query': {'geosearch': [None]}}),
    (lambda: wiki.random(), {'query': {'random': None}}),
    (lambda: wiki.languages(), {'query': {'languages': [None]}}),
])
def test_malformed_list_responses_are_typed(transport, call, data):
    transport.responses = [data]
    if 'searchinfo' in data['query']:
        # A valid searchinfo envelope may have statistics without a suggestion.
        assert call() is None
    else:
        with pytest.raises(wikipedia.RequestError):
            call()


def test_localized_category_prefix(transport):
    p = load(transport)
    transport.responses = [record(categories=[{'title': 'Catégorie:A:B'}])]
    assert p.categories == ['A:B']


@pytest.mark.parametrize('metadata', [{'url': 'not a list'}, [None], [{'url': 7}]])
def test_malformed_image_metadata(transport, metadata):
    p = load(transport)
    transport.responses = [{'query': {'pages': {'2': {'imageinfo': metadata}}}}]
    with pytest.raises(wikipedia.RequestError):
        p.images


def test_article_colon_not_a_namespace(transport):
    transport.responses = [record('Star Trek', pageprops={'disambiguation': ''}),
        {'parse': {'text': {'*': '<ul><li><a href="/wiki/Star_Trek:_Voyager">Voyager</a></li><li><a href="/wiki/Fichier:Image">Image</a></li></ul>'},
                   'links': [{'ns': 0, 'exists': '', '*': 'Star Trek: Voyager'}, {'ns': 6, 'exists': '', '*': 'Fichier:Image'}]}}]
    with pytest.raises(wikipedia.DisambiguationError) as exc:
        wiki.page('Star Trek', auto_suggest=False)
    assert exc.value.options == ['Star Trek: Voyager']


def test_page_property_lists_are_defensive(transport):
    p = load(transport)
    transport.responses = [record(links=[{'title': 'Moon'}])]
    p.links.append('mutated')
    assert p.links == ['Moon']
