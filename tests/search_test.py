# -*- coding: utf-8 -*-
import unittest

from collections import defaultdict

from wikipedia import wikipedia
from request_mock_data import mock_data


class TestSearch(unittest.TestCase):
  """Test the functionality of wikipedia.search."""

  def test_search(self):
    """Test parsing a Wikipedia request result."""
    self.assertEqual(wikipedia.search("Barack Obama"), mock_data['data']["barack.search"])

  def test_limit(self):
    """Test limiting a request results."""
    self.assertEqual(wikipedia.search("Porsche", results=3), mock_data['data']["porsche.search"])

  def test_suggestion(self):
    """Test getting a suggestion as well as search results."""
    search, suggestion = wikipedia.search("hallelulejah", suggestion=True)
    self.assertEqual(search, [])
    self.assertEqual(suggestion, u'hallelujah')

  def test_suggestion_none(self):
    """Test getting a suggestion when there is no suggestion."""
    search, suggestion = wikipedia.search("qmxjsudek", suggestion=True)
    self.assertEqual(search, [])
    self.assertEqual(suggestion, None)
