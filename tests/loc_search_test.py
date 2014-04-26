# -*- coding: utf-8 -*-
import unittest

from collections import defaultdict
from decimal import Decimal

from wikipedia import wikipedia
from request_mock_data import mock_data


# mock out _wiki_request
class _wiki_request(object):

  calls = defaultdict(int)

  @classmethod
  def __call__(cls, **params):
    cls.calls[params.__str__()] += 1
    return mock_data["_wiki_request calls"][tuple(sorted(params.items()))]

wikipedia._wiki_request = _wiki_request()


class TestSearchLoc(unittest.TestCase):
  """Test the functionality of wikipedia.search_loc."""

  def test_search_loc(self):
    """Test parsing a Wikipedia location request result."""
    self.assertEqual(
      wikipedia.search_loc(Decimal('40.67693'), Decimal('117.23193')),
      mock_data['data']["great_wall_of_china.geo_seach"]
    )

  def test_search_loc_with_radius(self):
    """Test parsing a Wikipedia location request result."""
    self.assertEqual(wikipedia.search_loc(
      Decimal('40.67693'), Decimal('117.23193'), radius=10000),
      mock_data['data']["great_wall_of_china.geo_seach_with_radius"]
    )

  def test_search_loc_with_existing_article_name(self):
    """Test parsing a Wikipedia location request result."""
    self.assertEqual(wikipedia.search_loc(
      Decimal('40.67693'), Decimal('117.23193'), article_name='Great Wall of China'),
      mock_data['data']["great_wall_of_china.geo_seach_with_existing_article_name"]
    )

  def test_search_loc_with_non_existing_article_name(self):
    self.assertEqual(wikipedia.search_loc(
      Decimal('40.67693'), Decimal('117.23193'), article_name='Test'),
      mock_data['data']["great_wall_of_china.geo_seach_with_non_existing_article_name"]
    )