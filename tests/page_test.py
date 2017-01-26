# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest

import mediawikiapi
from request_mock_data import mock_data

# mock out _wiki_request
def _wiki_request(params):
  return mock_data["_wiki_request calls"][tuple(sorted(params.items()))]
mediawikiapi._wiki_request = _wiki_request


class TestPage(unittest.TestCase):
  """Test the functionality of the rest of mediawikiapi.page."""

  def setUp(self):
    # shortest wikipedia articles with images and sections
    self.celtuce = mediawikiapi.page("Celtuce")
    self.cyclone = mediawikiapi.page("Tropical Depression Ten (2005)")
    self.great_wall_of_china = mediawikiapi.page("Great Wall of China")

  def test_from_page_id(self):
    """Test loading from a page id"""
    self.assertEqual(self.celtuce, mediawikiapi.page(pageid=1868108))

  def test_title(self):
    """Test the title."""
    self.assertEqual(self.celtuce.title, "Celtuce")
    self.assertEqual(self.cyclone.title, "Tropical Depression Ten (2005)")

  def test_url(self):
    """Test the url."""
    self.assertEqual(self.celtuce.url, "https://en.wikipedia.org/wiki/Celtuce")
    self.assertEqual(self.cyclone.url, "https://en.wikipedia.org/wiki/Tropical_Depression_Ten_(2005)")

  def test_content(self):
    """Test the plain text content."""
    self.assertEqual(self.celtuce.content, mock_data['data']["celtuce.content"])
    self.assertEqual(self.cyclone.content, mock_data['data']["cyclone.content"])
