# -*- coding: utf-8 -*-
import unittest

from collections import defaultdict

from wikipedia import wikipedia
from request_mock_data import mock_data

# mock out _wiki_request
class _wiki_request(object):

	calls = defaultdict(int)

	@classmethod
	def __call__(cls, **params):
		cls.calls[params.__str__()] += 1
		return mock_data["_wiki_request calls"][params.__str__()]

wikipedia._wiki_request = _wiki_request()

class TestSearch(unittest.TestCase):
	"""Test the functionality of wikipedia.search."""

	def test_search(self):
		"""Test parsing a Wikipedia request result."""
		self.assertEqual(wikipedia.search("Barack Obama"), mock_data['data']["barack.search"])
		self.assertEqual(_wiki_request.calls["{'list': 'search', 'srprop': '', 'srlimit': 10, 'limit': 10, 'srsearch': 'Barack Obama'}"], 1)

	def test_limit(self):
		"""Test limiting a request results."""
		self.assertEqual(wikipedia.search("Porsche", results=3), mock_data['data']["porsche.search"])
		self.assertEqual(_wiki_request.calls["{'list': 'search', 'srprop': '', 'srlimit': 3, 'limit': 3, 'srsearch': 'Porsche'}"], 1)

	def test_suggestion(self):
		"""Test getting a suggestion as well as search results."""
		search, suggestion = wikipedia.search("hallelulejah", suggestion=True)
		self.assertEqual(search, [])
		self.assertEqual(suggestion, u'hallelujah')

	def test_suggsetion_none(self):
		"""Test getting a suggestion when there is no suggestion."""
		search, suggestion = wikipedia.search("qmxjsudek", suggestion=True)
		self.assertEqual(search, [])
		self.assertEqual(suggestion, None)