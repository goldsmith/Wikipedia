# -*- coding: utf-8 -*-
import unittest
import pprint
from wikipedia import wikipedia_api

class TestData(unittest.TestCase):
  """Test the ability for wikipedia to change the language of the API being accessed."""

  def test_lang(self):
    wikipedia.set_wikidata_lang("en")
    self.assertEqual(wikipedia.API_URL, 'http://www.wikidata.org/w/api.php')

  def test_page(self):
    wikipedia.set_wikidata_lang("en")
    pprint.pprint(wikipedia.page('Q4989296'))
    

    
