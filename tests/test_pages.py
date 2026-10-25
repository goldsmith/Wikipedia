from decimal import Decimal
import pytest
import wikipedia
from wikipedia import wikipedia as wiki


def record(title="Earth", pageid="1", **fields):
    return {"query": {"pages": {str(pageid): {
        "pageid": int(pageid), "title": title, "fullurl": "https://en.wikipedia.org/wiki/" + title,
        **fields,
    }}}}


MISSING = {"query": {"pages": {"-1": {"title": "Missing", "missing": ""}}}}


def load(transport, **fields):
    transport.responses.append(record(**fields))
    return wiki.page("Earth", auto_suggest=False)


def test_exact_title_precedes_search(transport):
    transport.responses = [record()]
    p = wiki.page("Earth")
    assert p.title == "Earth"
    assert len(transport.calls) == 1
    assert transport.calls[0][1]["params"]["titles"] == "Earth"


def test_typo_fallback_is_bounded(transport):
    transport.responses = [MISSING, {"query": {"search": [], "searchinfo": {"suggestion": "Earth"}}}, record()]
    assert wiki.page("Erath").title == "Earth"
    assert len(transport.calls) == 3


def test_search_result_fallback(transport):
    transport.responses = [MISSING, {"query": {"search": [{"title": "Earth"}]}}, record()]
    assert wiki.page("Blue planet").title == "Earth"


def test_no_recursive_fallback(transport):
    transport.responses = [MISSING, {"query": {"search": [], "searchinfo": {"suggestion": "Also missing"}}}, MISSING]
    with pytest.raises(wikipedia.PageError):
        wiki.page("Missing")
    assert len(transport.calls) == 3


@pytest.mark.parametrize("auto_suggest", [False, True])
def test_missing_title_has_correct_exception(transport, auto_suggest):
    transport.responses = [MISSING, {"query": {"search": []}}]
    with pytest.raises(wikipedia.PageError) as exc:
        wiki.page("Missing", auto_suggest=auto_suggest)
    assert exc.value.title == "Missing"
    assert len(transport.calls) == (2 if auto_suggest else 1)


def test_empty_page_error_is_safe():
    assert isinstance(str(wikipedia.PageError("")), str)


@pytest.mark.parametrize("by_id", [False, True])
@pytest.mark.parametrize("allow", [False, True])
def test_normalized_redirect(transport, by_id, allow):
    response = record("United States")
    response["query"].update({"normalized": [{"from": "usa", "to": "USA"}],
                              "redirects": [{"from": "USA", "to": "United States"}]})
    transport.responses = [response]
    args = {"pageid": 1} if by_id else {"title": "usa"}
    if allow:
        assert wiki.page(**args, auto_suggest=False).title == "United States"
    else:
        with pytest.raises(wikipedia.RedirectError):
            wiki.page(**args, auto_suggest=False, redirect=False)
    assert len(transport.calls) == 1


def test_page_language_is_bound(transport):
    p = load(transport)
    wiki.set_lang("fr")
    transport.responses = [record(extract="English"), record(links=[]),
                           {"parse": {"text": {"*": "<p>English</p>"}}}]
    assert p.summary == "English"
    assert p.links == []
    assert p.html() == "<p>English</p>"
    assert all(url.startswith("https://en.") for url, _ in transport.calls)


@pytest.mark.parametrize("prop,api", [("links", "links"), ("references", "extlinks"), ("categories", "categories"), ("coordinates", "coordinates")])
def test_missing_property_is_cached(transport, prop, api):
    p = load(transport)
    transport.responses = [record()]
    expected = None if prop == "coordinates" else []
    assert getattr(p, prop) == expected
    assert getattr(p, prop) == expected
    assert len(transport.calls) == 2


def test_empty_images_generator(transport):
    p = load(transport)
    transport.responses = [{"batchcomplete": ""}]
    assert p.images == []
    assert p.images == []
    assert len(transport.calls) == 2


def test_images_skip_missing_file_url(transport):
    p = load(transport)
    transport.responses = [{"query": {"pages": {"2": {"imageinfo": [{}]}, "3": {"imageinfo": [{"url": "https://example.org/a.png"}]}}}}]
    assert p.images == ["https://example.org/a.png"]


def test_links_continuation(transport):
    p = load(transport)
    first = record(links=[{"title": "Moon"}]); first["continue"] = {"plcontinue": "1|0|Mars", "continue": "||"}
    transport.responses = [first, record(links=[{"title": "Mars"}])]
    assert p.links == ["Moon", "Mars"]
    assert transport.calls[-1][1]["params"]["plcontinue"] == "1|0|Mars"


def test_continuation_failure_never_caches_partial_results(transport):
    p = load(transport)
    first = record(links=[{"title": "Moon"}]); first["continue"] = {"plcontinue": "next"}
    transport.responses = [first, {"error": {"code": "badcontinue", "info": "bad continuation"}}]
    with pytest.raises(wikipedia.RequestError):
        p.links
    assert not hasattr(p, "_links")
    transport.responses = [record(links=[{"title": "Mars"}])]
    assert p.links == ["Mars"]


def test_repeated_continuation_is_rejected(transport):
    p = load(transport)
    first = record(links=[]); first["continue"] = {"plcontinue": "same"}
    transport.responses = [first, first]
    with pytest.raises(wikipedia.RequestError, match="continuation"):
        p.links
    assert len(transport.calls) == 3


@pytest.mark.parametrize("data", [{"query": {}}, {"query": {"pages": []}}, {"query": {"pages": {"2": {}}}}, {"query": {"pages": {"1": {"links": None}}}}])
def test_malformed_page_property_is_not_empty_result(transport, data):
    p = load(transport)
    transport.responses = [data]
    with pytest.raises(wikipedia.RequestError):
        p.links


def test_disambiguation_uses_link_targets(transport):
    transport.responses = [record("Mercury", pageprops={"disambiguation": ""}),
        {"parse": {"text": {"*": '<ul><li><a href="/wiki/Mercury_(planet)">the planet</a></li><li><a href="/wiki/Mercury_(element)#History">chemical element</a></li><li><a href="/wiki/File:X">image</a></li><li><a class="new" href="/w/index.php?title=Missing&amp;redlink=1">missing</a></li></ul>'},
                   "links": [{"ns": 0, "exists": "", "*": "Mercury (planet)"}, {"ns": 0, "exists": "", "*": "Mercury (element)"}, {"ns": 6, "exists": "", "*": "File:X"}]}}]
    with pytest.raises(wikipedia.DisambiguationError) as exc:
        wiki.page("Mercury")
    assert exc.value.options == ["Mercury (planet)", "Mercury (element)"]
    assert transport.calls[-1][1]["params"]["action"] == "parse"


def test_non_disambiguation_pageprops(transport):
    transport.responses = [record(pageprops={"wikibase_item": "Q2"})]
    assert wiki.page("Earth", auto_suggest=False).title == "Earth"


def test_sections_tocdata_decodes_headings(transport):
    p = load(transport)
    transport.responses = [{"parse": {"tocdata": {"sections": [{"line": "Early <i>history</i> &amp; origins"}, {"line": "日本語"}]}}}]
    assert p.sections == ["Early history & origins", "日本語"]
    assert transport.calls[-1][1]["params"]["prop"] == "tocdata"


def test_section_boundaries_are_heading_lines(transport):
    p = load(transport)
    p._content = "Lead\n== A ==\nText with == inline equality.\n=== Nested ===\nChild.\n== A long title ==\nOther.\n== Last ==\nFinal."
    assert p.section("A") == "Text with == inline equality."
    assert p.section("Nested") == "Child."
    assert p.section("Last") == "Final."
    assert p.section("long title") is None


def test_references_preserve_non_http_schemes(transport):
    p = load(transport)
    transport.responses = [record(extlinks=[{"*": "https://example.org"}, {"*": "//example.org/path"}, {"*": "mailto:editor@example.org"}, {"*": "ftp://example.org/file"}])]
    assert p.references == ["https://example.org", "https://example.org/path", "mailto:editor@example.org", "ftp://example.org/file"]


def test_coordinates_remain_decimals(transport):
    p = load(transport)
    transport.responses = [record(coordinates=[{"lat": 1.5, "lon": 2.25}])]
    assert p.coordinates == (Decimal("1.5"), Decimal("2.25"))


def test_summary_positional_sentences_and_resolved_page(transport):
    transport.responses = [record(), record(extract="Two sentences. Like this.")]
    assert wiki.summary("Earth", 2) == "Two sentences. Like this."
    assert transport.calls[-1][1]["params"]["exsentences"] == 2


def test_preload_and_empty_text_only_fetch_once(transport):
    transport.responses = [record(), record(extract="", revisions=[{"revid": 10, "parentid": 9}]),
        record(extract=""), {"batchcomplete": ""}, record(), record(),
        {"parse": {"tocdata": {"sections": []}}}]
    p = wiki.page("Earth", auto_suggest=False, preload=True)
    assert p.content == p.summary == ""
    assert p.revision_id == 10 and p.parent_id == 9
    assert p.images == p.references == p.links == p.sections == []
    assert len(transport.calls) == 7


def test_equality_does_not_swallow_interrupt(transport):
    p = load(transport)
    class Interrupted:
        @property
        def pageid(self):
            raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        p == Interrupted()
