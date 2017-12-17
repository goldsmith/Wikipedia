# -*- coding: utf-8 -*-
import unittest

from mediawikiapi import LanguageError
from mediawikiapi import Language


class TestLanguage(unittest.TestCase):
  """Test the Language class"""

  def setUp(self):
    self.lang_class = Language()

  def test_default_language(self):
    """ Test that default language set to en"""
    self.assertEqual(self.lang_class.language, 'en')
  
  def test_set_language(self):  
    """ Test the set language"""
    self.lang_class.language = 'fr'
    self.assertEqual(self.lang_class.language, 'fr')

  def test_set_fake_language(self):
    """ Test exception when try to set wrong language"""
    with self.assertRaises(LanguageError):
      self.lang_class.language = 'fakelang'
