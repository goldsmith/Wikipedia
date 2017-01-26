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

  def test_sections(self):
    """Test the list of section titles."""
    print("cyclone.sections")
    print(self.cyclone.sections)
    print(self.cyclone.title)
    self.assertCountEqual(sorted(self.cyclone.sections), mock_data['data']["cyclone.sections"])

  def test_section(self):
    """Test text content of a single section."""
    self.assertEqual(self.cyclone.section("Impact"), mock_data['data']["cyclone.section.impact"])
    self.assertEqual(self.cyclone.section("History"), None)

