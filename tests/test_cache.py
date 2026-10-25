import pytest
from wikipedia import wikipedia as wiki
from wikipedia import util


def test_geosearch_invalidated_by_language(transport):
    transport.responses = [{"query": {"geosearch": [{"title": "English"}]}}, {"query": {"geosearch": [{"title": "Français"}]}}]
    assert wiki.geosearch(1, 2) == ["English"]
    wiki.set_lang("fr")
    assert wiki.geosearch(1, 2) == ["Français"]


def test_cached_lists_and_dicts_are_isolated(transport):
    transport.responses = [{"query": {"search": [{"title": "Earth"}]}}, {"query": {"languages": [{"code": "en", "*": "English"}]}}]
    wiki.search("Earth").append("mutated")
    assert wiki.search("Earth") == ["Earth"]
    wiki.languages()["en"] = "mutated"
    assert wiki.languages() == {"en": "English"}
    assert len(transport.calls) == 2


def test_cache_expires(monkeypatch):
    now = [0.0]
    monkeypatch.setattr(wiki.time, "monotonic", lambda: now[0])
    calls = []
    @util.cache
    def fn(value):
        calls.append(value)
        return len(calls)
    assert fn(1) == 1
    now[0] = 299
    assert fn(1) == 1
    now[0] = 300
    assert fn(1) == 2


def test_cache_bounded_lru_and_clear():
    calls = []
    @util.cache
    def fn(value):
        calls.append(value)
        return value
    for i in range(256):
        fn(i)
    fn(0)
    fn(256)
    assert len(fn._cache) == 256
    fn(0)
    assert len(calls) == 257
    fn(1)
    assert len(calls) == 258
    fn.clear_cache()
    assert not fn._cache


def test_failed_calls_not_cached():
    calls = []
    @util.cache
    def fn():
        calls.append(1)
        raise ValueError("failed")
    for _ in range(2):
        with pytest.raises(ValueError):
            fn()
    assert len(calls) == 2
