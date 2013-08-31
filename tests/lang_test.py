# -*- coding: utf-8 -*-
import unittest
import requests

from wikipedia import wikipedia

class TestLang(unittest.TestCase):
    """Test the ability for wikipedia to change the language of the API being accessed."""

    def test_lang(self):
        wikipedia.set_lang("fr")
        self.assertEqual(wikipedia.api_url, 'http://fr.wikipedia.org/w/api.php')
    