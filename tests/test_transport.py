from datetime import timedelta
from email.utils import formatdate
import pytest
import requests
import wikipedia
from wikipedia import wikipedia as wiki
from tests.conftest import Response


OK = {"query": {"search": []}}


def test_https_session_timeout_headers_and_immutable_params(transport, monkeypatch):
    monkeypatch.setattr(wiki.requests, "get", lambda *a, **k: pytest.fail("must reuse Session"))
    wiki.set_user_agent("Example/1.0 (https://example.org/contact)")
    transport.responses = [OK]
    params = {"list": "search", "srsearch": "Earth"}
    assert wiki._wiki_request(params) == OK
    url, kwargs = transport.calls[0]
    assert url == "https://en.wikipedia.org/w/api.php"
    assert kwargs["timeout"] == (5, 15)
    assert kwargs["headers"]["User-Agent"].startswith("Example/1.0")
    assert "format" not in params and "action" not in params


@pytest.mark.parametrize("timeout", [3, 0.1, (2, 4), None])
def test_configurable_timeout(transport, timeout):
    wikipedia.set_timeout(timeout)
    transport.responses = [OK]
    wiki._wiki_request({})
    assert transport.calls[0][1]["timeout"] == timeout


@pytest.mark.parametrize("timeout", [0, -1, True, float("nan"), float("inf"), "5", (0, 1), (1,), (1, 2, 3), [1, 2]])
def test_invalid_timeout(timeout):
    with pytest.raises(ValueError):
        wikipedia.set_timeout(timeout)


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_transient_http_retry(transport, status):
    transport.responses = [Response(status=status), Response(status=status), OK]
    assert wiki._wiki_request({}) == OK
    assert len(transport.calls) == 3
    assert transport.sleeps == ([5, 10] if status == 429 else [1, 2])


@pytest.mark.parametrize("code", ["maxlag", "ratelimited"])
def test_transient_api_retry(transport, code):
    transport.responses = [{"error": {"code": code, "info": "busy"}}, OK]
    assert wiki._wiki_request({}) == OK
    assert transport.sleeps == [5]


@pytest.mark.parametrize("error_type", [requests.ConnectionError, requests.Timeout])
def test_transport_retry(transport, error_type):
    transport.responses = [error_type("temporary"), OK]
    assert wiki._wiki_request({}) == OK
    assert transport.sleeps == [1]


def test_exhausted_timeout_preserves_exception(transport):
    transport.responses = [requests.Timeout("slow")] * 3
    with pytest.raises(wikipedia.HTTPTimeoutError) as exc:
        wiki._wiki_request({"titles": "Earth"})
    assert exc.value.query == "Earth"
    assert len(transport.calls) == 3


def test_exhausted_connection_is_typed(transport):
    transport.responses = [requests.ConnectionError("offline")] * 3
    with pytest.raises(wikipedia.RequestError):
        wiki._wiki_request({})
    assert len(transport.calls) == 3


def test_exhausted_http_has_status(transport):
    transport.responses = [Response(status=503)] * 3
    with pytest.raises(wikipedia.RequestError) as exc:
        wiki._wiki_request({})
    assert exc.value.status_code == 503
    assert exc.value.api_code is None


def test_api_error_has_code_and_is_not_retried(transport):
    transport.responses = [{"error": {"code": "badvalue", "info": "bad parameter"}}]
    with pytest.raises(wikipedia.RequestError) as exc:
        wiki._wiki_request({})
    assert exc.value.api_code == "badvalue"
    assert exc.value.status_code == 200
    assert "bad parameter" in str(exc.value)
    assert not transport.sleeps


def test_retry_after_seconds(transport):
    transport.responses = [Response(status=503, headers={"Retry-After": "7"}), OK]
    wiki._wiki_request({})
    assert transport.sleeps == [7]


def test_retry_after_date(transport, monkeypatch):
    monkeypatch.setattr(wiki.time, "time", lambda: 1_700_000_000)
    transport.responses = [Response(status=429, headers={"Retry-After": formatdate(1_700_000_008, usegmt=True)}), OK]
    wiki._wiki_request({})
    assert transport.sleeps == [8]


@pytest.mark.parametrize("delays,calls,sleeps", [(["31"], 1, []), (["20", "20"], 2, [20])])
def test_retry_sleep_budget(transport, delays, calls, sleeps):
    transport.responses = [Response(status=429, headers={"Retry-After": d}) for d in delays]
    with pytest.raises(wikipedia.RequestError) as exc:
        wiki._wiki_request({})
    assert exc.value.retry_after == float(delays[-1])
    assert len(transport.calls) == calls
    assert transport.sleeps == sleeps


@pytest.mark.parametrize("data", [ValueError("bad json"), [], None, "html", {"query": []}, {"unrelated": True}])
def test_malformed_response_is_typed(transport, data):
    transport.responses = [Response(data)]
    with pytest.raises(wikipedia.RequestError):
        wiki._wiki_request({})
    assert len(transport.calls) == 1


def test_permanent_http_does_not_retry(transport):
    transport.responses = [Response(ValueError("not JSON"), status=403)]
    with pytest.raises(wikipedia.RequestError) as exc:
        wiki._wiki_request({})
    assert exc.value.status_code == 403
    assert not transport.sleeps


def test_fractional_rate_limit_uses_monotonic(transport, monkeypatch):
    monkeypatch.setattr(wiki.time, "monotonic", lambda: 10.0)
    wiki.set_rate_limiting(True, timedelta(milliseconds=50))
    transport.responses = [OK, OK]
    wiki._wiki_request({})
    wiki._wiki_request({})
    assert transport.sleeps == pytest.approx([0.05])


def test_keyboard_interrupt_not_swallowed(transport):
    transport.responses = [KeyboardInterrupt()]
    with pytest.raises(KeyboardInterrupt):
        wiki._wiki_request({})
