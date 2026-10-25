"""Contracts shared with the released 1.4.0 API."""
import inspect
from decimal import Decimal
import pytest
import wikipedia
from wikipedia import wikipedia as wiki


@pytest.mark.parametrize("name,parameters", [
    ("search", ["query", "results", "suggestion"]),
    ("suggest", ["query"]),
    ("summary", ["title", "sentences", "chars", "auto_suggest", "redirect"]),
    ("page", ["title", "pageid", "auto_suggest", "redirect", "preload"]),
    ("geosearch", ["latitude", "longitude", "title", "results", "radius"]),
    ("random", ["pages"]),
    ("WikipediaPage", ["title", "pageid", "redirect", "preload", "original_title"]),
])
def test_public_positional_contract(name, parameters):
    assert list(inspect.signature(getattr(wikipedia, name)).parameters) == parameters
    assert getattr(wikipedia, name) is getattr(wiki, name)


def test_exception_attributes_and_version():
    assert len(wikipedia.__version__) == 3
    assert isinstance(wikipedia.__version__, tuple)
    error = wikipedia.DisambiguationError("Mercury", ["Mercury (planet)"])
    assert error.title == "Mercury" and error.options == ["Mercury (planet)"]
    assert wikipedia.RedirectError("USA").title == "USA"
    assert wikipedia.HTTPTimeoutError("Earth").query == "Earth"
    assert wikipedia.PageError(pageid=42).pageid == 42
    assert wikipedia.WikipediaException("bad").error == "bad"


def test_search_suggest_languages_random_shapes(transport):
    transport.responses = [
        {"query": {"search": [{"title": "Earth"}]}},
        {"query": {"search": [], "searchinfo": {"suggestion": "Earth"}}},
        {"query": {"searchinfo": {"suggestion": "Earth"}}},
        {"query": {"languages": [{"code": "en", "*": "English"}]}},
        {"query": {"random": [{"title": "Earth"}]}},
        {"query": {"random": [{"title": "Earth"}, {"title": "Mars"}]}},
    ]
    assert wikipedia.search("Earth", 1) == ["Earth"]
    assert wikipedia.search("Eart", 1, True) == ([], "Earth")
    assert wikipedia.suggest("Eart") == "Earth"
    assert wikipedia.languages() == {"en": "English"}
    assert wikipedia.random() == "Earth"
    assert wikipedia.random(2) == ["Earth", "Mars"]
    assert not transport.responses


def test_page_missing_arguments():
    with pytest.raises(ValueError):
        wikipedia.page()
