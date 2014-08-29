# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest

from wikipedia import wikipedia
from request_mock_data import mock_data


# mock out _wiki_request
def _wiki_request(params):
  return mock_data["_wiki_request calls"][tuple(sorted(params.items()))]
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

  def test_redirect_no_normalization(self):
    """Test that a page with redirects but no normalization query loads correctly"""
    the_party = wikipedia.page("Communist Party", auto_suggest=False)
    self.assertIsInstance(the_party, wikipedia.WikipediaPage)
    self.assertEqual(the_party.title, "Communist party")

  def test_redirect_with_normalization(self):
    """Test that a page redirect with a normalized query loads correctly"""
    the_party = wikipedia.page("communist Party", auto_suggest=False)
    self.assertIsInstance(the_party, wikipedia.WikipediaPage)
    self.assertEqual(the_party.title, "Communist party")

  def test_redirect_normalization(self):
    """Test that a page redirect loads correctly with or without a query normalization"""
    capital_party = wikipedia.page("Communist Party", auto_suggest=False)
    lower_party = wikipedia.page("communist Party", auto_suggest=False)

    self.assertIsInstance(capital_party, wikipedia.WikipediaPage)
    self.assertIsInstance(lower_party, wikipedia.WikipediaPage)
    self.assertEqual(capital_party.title, "Communist party")
    self.assertEqual(capital_party, lower_party)

  def test_disambiguate(self):
    """Test that page raises an error when a disambiguation page is reached."""
    try:
      ram = wikipedia.page("Dodge Ram (disambiguation)", auto_suggest=False, redirect=False)
      error_raised = False
    except wikipedia.DisambiguationError as e:
      error_raised = True
      options = e.options

    self.assertTrue(error_raised)
    self.assertEqual(options, [u'Dodge Ramcharger', u'Dodge Ram Van', u'Dodge Mini Ram', u'Dodge Caravan C/V', u'Dodge Caravan C/V', u'Ram C/V', u'Dodge Ram 50', u'Dodge D-Series', u'Dodge Rampage', u'Ram (brand)'])

  def test_auto_suggest(self):
    """Test that auto_suggest properly corrects a typo."""
    # yum, butter.
    butterfly = wikipedia.page("butteryfly")

    self.assertEqual(butterfly.title, "Butterfly")
    self.assertEqual(butterfly.url, "http://en.wikipedia.org/wiki/Butterfly")


class TestPage(unittest.TestCase):
  """Test the functionality of the rest of wikipedia.page."""

  def setUp(self):
    # shortest wikipedia articles with images and sections
    self.celtuce = wikipedia.page("Celtuce")
    self.cyclone = wikipedia.page("Tropical Depression Ten (2005)")
    self.great_wall_of_china = wikipedia.page("Great Wall of China")

  def test_from_page_id(self):
    """Test loading from a page id"""
    self.assertEqual(self.celtuce, wikipedia.page(pageid=1868108))

  def test_title(self):
    """Test the title."""
    self.assertEqual(self.celtuce.title, "Celtuce")
    self.assertEqual(self.cyclone.title, "Tropical Depression Ten (2005)")

  def test_url(self):
    """Test the url."""
    self.assertEqual(self.celtuce.url, "http://en.wikipedia.org/wiki/Celtuce")
    self.assertEqual(self.cyclone.url, "http://en.wikipedia.org/wiki/Tropical_Depression_Ten_(2005)")

  def test_content(self):
    """Test the plain text content."""
    self.assertEqual(self.celtuce.content, mock_data['data']["celtuce.content"])
    self.assertEqual(self.cyclone.content, mock_data['data']["cyclone.content"])

  def test_revision_id(self):
    """Test the revision id."""
    self.assertEqual(self.celtuce.revision_id, mock_data['data']["celtuce.revid"])
    self.assertEqual(self.cyclone.revision_id, mock_data['data']["cyclone.revid"])

  def test_parent_id(self):
    """Test the parent id."""
    self.assertEqual(self.celtuce.parent_id, mock_data['data']["celtuce.parentid"])
    self.assertEqual(self.cyclone.parent_id, mock_data['data']["cyclone.parentid"])


  def test_summary(self):
    """Test the summary."""
    self.assertEqual(self.celtuce.summary, mock_data['data']["celtuce.summary"])
    self.assertEqual(self.cyclone.summary, mock_data['data']["cyclone.summary"])

  def test_images(self):
    """Test the list of image URLs."""
    self.assertEqual(sorted(self.celtuce.images), mock_data['data']["celtuce.images"])
    self.assertEqual(sorted(self.cyclone.images), mock_data['data']["cyclone.images"])

  def test_references(self):
    """Test the list of reference URLs."""
    self.assertEqual(self.celtuce.references, mock_data['data']["celtuce.references"])
    self.assertEqual(self.cyclone.references, mock_data['data']["cyclone.references"])

  def test_links(self):
    """Test the list of titles of links to Wikipedia pages."""
    self.assertEqual(self.celtuce.links, mock_data['data']["celtuce.links"])
    self.assertEqual(self.cyclone.links, mock_data['data']["cyclone.links"])

  def test_categories(self):
    """Test the list of categories of Wikipedia pages."""
    self.assertEqual(self.celtuce.categories, mock_data['data']["celtuce.categories"])
    self.assertEqual(self.cyclone.categories, mock_data['data']["cyclone.categories"])

  def test_html(self):
    """Test the full HTML method."""
    self.assertEqual(self.celtuce.html(), mock_data['data']["celtuce.html"])

  def test_sections(self):
    """Test the list of section titles."""
    self.assertEqual(sorted(self.cyclone.sections), mock_data['data']["cyclone.sections"])

  def test_section(self):
    """Test text content of a single section."""
    self.assertEqual(self.cyclone.section("Impact"), mock_data['data']["cyclone.section.impact"])
    self.assertEqual(self.cyclone.section("History"), None)

  def test_coordinates(self):
    """Test geo coordinates of a page"""
    lat, lon = self.great_wall_of_china.coordinates
    self.assertEqual(str(lat.quantize(Decimal('1.000'))), mock_data['data']['great_wall_of_china.coordinates.lat'])
    self.assertEqual(str(lon.quantize(Decimal('1.000'))), mock_data['data']['great_wall_of_china.coordinates.lon'])
