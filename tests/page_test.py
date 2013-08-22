# -*- coding: utf-8 -*-
import unittest

from collections import defaultdict

from wikipedia import wikipedia
from request_mock_data import mock_data

# mock out _wiki_request
def _wiki_request(**params):
	return mock_data["_wiki_request calls"][params.__str__()]
wikipedia._wiki_request = _wiki_request

class TestPageSetUp(unittest.TestCase):
	"""Test the functionality of wikipedia.page's __init__ and load functions."""

	def test_missing(self):
		"""Test that page raises a PageError for a nonexistant page."""
		# Callicarpa?
		purpleberry = lambda: wikipedia.page("purpleberry", auto_suggest=False)
		self.assertRaises(wikipedia.PageError, purpleberry)

	def test_redirect_true(self):
		"""Test that a page successfully redirects a query."""
		# no error should be raised if redirect is test_redirect_true
		mp = wikipedia.page("Menlo Park, New Jersey")

		self.assertEqual(mp.title, "Edison, New Jersey")
		self.assertEqual(mp.url, "http://en.wikipedia.org/wiki/Edison,_New_Jersey")

	def test_redirect_false(self):
		"""Test that page raises an error on a redirect when redirect == False."""
		mp = lambda: wikipedia.page("Menlo Park, New Jersey", auto_suggest=False, redirect=False)
		self.assertRaises(wikipedia.RedirectError, mp)

	def test_disambiguate(self):
		"""Test that page raises an error when a disambiguation page is reached."""
		try:
			ram = wikipedia.page("Dodge Ram (disambiguation)", auto_suggest=False, redirect=False)
			error_raised = False
		except wikipedia.DisambiguationError as e:
			error_raised = True
			options = e.options

		self.assertTrue(error_raised)
		self.assertEqual(options, [u'Dodge Ramcharger', u'Dodge Ram Van', u'Dodge Mini Ram', u'Dodge Caravan C/V', u'Dodge Caravan C/V', u'Ram C/V', u'Dodge Ram 50'])

	def test_auto_suggest(self):
		"""Test that auto_suggest properly corrects a typo."""
		# yum, butter.
		butterfly = wikipedia.page("butteryfly")

		self.assertEqual(butterfly.title, "butterfly")
		self.assertEqual(butterfly.url, "http://en.wikipedia.org/wiki/Butterfly")

class TestPage(unittest.TestCase):
	"""Test the functionality of the rest of wikipedia.page."""

	def setUp(self):
		# one of the shortest wikipedia articles that includes images
		self.celtuce = wikipedia.page("Celtuce")

	def test_title(self):
		"""Test the title."""
		self.assertEqual(self.celtuce.title, "Celtuce")

	def test_url(self):
		"""Test the url."""
		self.assertEqual(self.celtuce.url, "http://en.wikipedia.org/wiki/Celtuce")

	def test_content(self):
		"""Test the plain text content."""
		self.assertEqual(self.celtuce.content, mock_data['data']["celtuce.content"])

	def test_summary(self):
		"""Test the summary."""
		self.assertEqual(self.celtuce.summary, mock_data['data']["celtuce.summary"])

	def test_images(self):
		"""Test the list of image URLs."""
		self.assertEqual(self.celtuce.images, mock_data['data']["celtuce.images"])

	def test_references(self):
		"""Test the list of reference URLs."""
		self.assertEqual(self.celtuce.references, mock_data['data']["celtuce.references"])