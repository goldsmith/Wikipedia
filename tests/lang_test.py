# -*- coding: utf-8 -*-
import unittest

from mediawikiapi import set_lang, config


class TestLang(unittest.TestCase):
  """Test the ability for mediawikiapi to change the language of the API being accessed."""

  def test_lang(self):  
    set_lang("fr")
    self.assertEqual(config.get_api_url(), 'https://fr.wikipedia.org/w/api.php')
