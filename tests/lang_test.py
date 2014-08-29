# -*- coding: utf-8 -*-
import unittest

from wikipedia import exceptions
from wikipedia import wikipedia


class TestLang(unittest.TestCase):

    """Test the ability for wikipedia to change the language of the API being accessed."""

    def test_correct_lang(self):
        wikipedia.set_lang("fr")
        self.assertEqual(
            wikipedia.API_URL, 'http://fr.wikipedia.org/w/api.php')
        
    def test_fake_lang(self):
        self.assertRaises(exceptions.LanguageError, wikipedia.set_lang,"fakelang")
