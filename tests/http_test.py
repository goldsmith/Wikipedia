# -*- coding: utf-8 -*-
"""Tests for the HTTP layer (_http_get_json) and auto_suggest, with the network mocked."""
import unittest
from datetime import datetime, timedelta

from unittest import mock

import requests

from wikipedia import wikipedia
from wikipedia.exceptions import HTTPTimeoutError, WikipediaException


def _response(status=200, json_body=None, headers=None):
  r = mock.Mock()
  r.status_code = status
  r.headers = headers or {}
  if json_body is not None:
    r.json.return_value = json_body
  else:
    r.json.side_effect = ValueError('No JSON object could be decoded')
  return r


class HttpTestCase(unittest.TestCase):

  def setUp(self):
    self.session = mock.Mock()
    self.patches = [
      mock.patch.object(wikipedia, '_get_session', return_value=self.session),
      mock.patch.object(wikipedia.time, 'sleep'),
    ]
    self.sleep = None
    for p in self.patches:
      started = p.start()
      if p.attribute == 'sleep':
        self.sleep = started
    self.saved = (wikipedia.API_URL, wikipedia.REQUEST_TIMEOUT, wikipedia.RATE_LIMIT,
                  wikipedia.RATE_LIMIT_MIN_WAIT, wikipedia.RATE_LIMIT_LAST_CALL)
    wikipedia.API_URL = 'https://en.wikipedia.org/w/api.php'

  def tearDown(self):
    for p in self.patches:
      p.stop()
    (wikipedia.API_URL, wikipedia.REQUEST_TIMEOUT, wikipedia.RATE_LIMIT,
     wikipedia.RATE_LIMIT_MIN_WAIT, wikipedia.RATE_LIMIT_LAST_CALL) = self.saved


class TestRequests(HttpTestCase):

  def test_uses_https_json_user_agent_and_timeout(self):
    self.session.get.return_value = _response(json_body={'ok': 1})
    self.assertEqual(wikipedia._http_get_json({'list': 'search'}), {'ok': 1})

    args, kwargs = self.session.get.call_args
    self.assertEqual(args[0], 'https://en.wikipedia.org/w/api.php')
    self.assertEqual(kwargs['params'], {'list': 'search', 'format': 'json', 'action': 'query'})
    self.assertEqual(kwargs['timeout'], 30)
    ua = kwargs['headers']['User-Agent']
    self.assertIn('https://github.com/goldsmith/Wikipedia/', ua)
    self.assertIn('python-requests/', ua)

  def test_set_lang_keeps_https(self):
    wikipedia.set_lang('de')
    self.assertEqual(wikipedia.API_URL, 'https://de.wikipedia.org/w/api.php')

  def test_set_timeout(self):
    wikipedia.set_timeout(5)
    self.session.get.return_value = _response(json_body={})
    wikipedia._http_get_json({})
    self.assertEqual(self.session.get.call_args[1]['timeout'], 5)

  def test_timeout_raises_http_timeout_error(self):
    self.session.get.side_effect = requests.exceptions.ReadTimeout()
    with self.assertRaises(HTTPTimeoutError) as ctx:
      wikipedia._http_get_json({'srsearch': 'Barack Obama'})
    self.assertEqual(ctx.exception.query, 'Barack Obama')

  def test_retries_429_honouring_retry_after(self):
    self.session.get.side_effect = [
      _response(429, headers={'Retry-After': '3'}),
      _response(json_body={'ok': 1}),
    ]
    self.assertEqual(wikipedia._http_get_json({}), {'ok': 1})
    self.assertEqual(self.session.get.call_count, 2)
    self.sleep.assert_called_once_with(3.0)

  def test_retries_5xx_with_backoff_then_reports_non_json(self):
    self.session.get.return_value = _response(503)
    with self.assertRaises(WikipediaException) as ctx:
      wikipedia._http_get_json({'titles': 'Python'})
    self.assertEqual(self.session.get.call_count, 1 + wikipedia.MAX_RETRIES)
    self.assertEqual([c[0][0] for c in self.sleep.call_args_list], [1, 2])
    self.assertIn('HTTP 503', str(ctx.exception.error))

  def test_retry_after_is_capped(self):
    self.assertEqual(wikipedia._backoff(0, '3600'), wikipedia.RETRY_MAX_WAIT)
    self.assertEqual(wikipedia._backoff(3, None), 8)
    self.assertEqual(wikipedia._backoff(0, 'Wed, 21 Oct 2015 07:28:00 GMT'), 1)

  def test_connection_errors_are_retried_then_raised(self):
    self.session.get.side_effect = requests.exceptions.ConnectionError('reset')
    with self.assertRaises(requests.exceptions.ConnectionError):
      wikipedia._http_get_json({})
    self.assertEqual(self.session.get.call_count, 1 + wikipedia.MAX_RETRIES)

  def test_client_errors_are_not_retried(self):
    self.session.get.return_value = _response(404)
    with self.assertRaises(WikipediaException):
      wikipedia._http_get_json({})
    self.assertEqual(self.session.get.call_count, 1)

  def test_rate_limit_waits_for_sub_second_intervals(self):
    """Regression: int(total_seconds()) turned the default 50 ms wait into 0."""
    wikipedia.set_rate_limiting(True, min_wait=timedelta(milliseconds=500))
    wikipedia.RATE_LIMIT_LAST_CALL = datetime.now()
    self.session.get.return_value = _response(json_body={})
    wikipedia._http_get_json({})
    waited = self.sleep.call_args[0][0]
    self.assertGreater(waited, 0.3)
    self.assertLessEqual(waited, 0.5)


class TestAutoSuggest(unittest.TestCase):

  def _page(self, title, results, suggestion):
    with mock.patch.object(wikipedia, 'search', return_value=(results, suggestion)), \
         mock.patch.object(wikipedia, 'WikipediaPage') as page_cls:
      wikipedia.page(title)
      return page_cls.call_args[0][0]

  def test_exact_title_is_not_replaced_by_the_suggestion(self):
    self.assertEqual(self._page('Dune', ['Dune'], 'dunes'), 'Dune')
    self.assertEqual(self._page('dune', ['Dune'], 'dunes'), 'Dune')

  def test_typos_still_use_the_suggestion(self):
    self.assertEqual(self._page('butteryfly', ["Butterfly's Tongue"], 'butterfly'), 'butterfly')

  def test_top_result_when_no_suggestion(self):
    self.assertEqual(self._page('Menlo Park', ['Menlo Park, California'], None), 'Menlo Park, California')

  def test_nothing_found_raises_page_error(self):
    with mock.patch.object(wikipedia, 'search', return_value=([], None)):
      self.assertRaises(wikipedia.PageError, wikipedia.page, 'qmxjsudek')


if __name__ == '__main__':
  unittest.main()
