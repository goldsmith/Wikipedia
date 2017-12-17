# -*- coding: utf-8 -*-
import unittest

from collections import defaultdict

from mediawikiapi import MediaWikiAPI
from request_mock_data import mock_data


# mock out _wiki_request
class _wiki_request(object):

  calls = defaultdict(int)

  @classmethod
  def __call__(cls, params):
    cls.calls[params.__str__()] += 1
    return mock_data["_wiki_request calls"][tuple(sorted(params.items()))]

api = MediaWikiAPI()
api.wiki_request.request = _wiki_request()


class TestSearch(unittest.TestCase):
  """Test the functionality of mediawikiapi.search."""

  def test_search(self):
    """Test parsing a mediawikiapi request result."""
    self.assertEqual(api.search("Barack Obama"), mock_data['data']["barack.search"])

  def test_limit(self):
    """Test limiting a request results."""
    self.assertEqual(api.search("Porsche", results=3), mock_data['data']["porsche.search"])

  def test_suggestion(self):
    """Test getting a suggestion as well as search results."""
    search, suggestion = api.search("hallelulejah", suggestion=True)
    self.assertEqual(search, [])
    self.assertEqual(suggestion, u'hallelujah')

  def test_suggestion_none(self):
    """Test getting a suggestion when there is no suggestion."""
    search, suggestion = api.search("qmxjsudek", suggestion=True)
    self.assertEqual(search, [])
    self.assertEqual(suggestion, None)
