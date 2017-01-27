# -*- coding: utf-8 -*-
import unittest

import mediawikiapi

class TestSession(unittest.TestCase):
  
  def test_new_session(self):
    """ Test the new_session function """
    mediawikiapi.config.new_session()
    s1 = mediawikiapi.config.get_session()
    self.assertIsNotNone(s1)

    mediawikiapi.config.new_session()
    s2 = mediawikiapi.config.get_session()
    self.assertIsNotNone(s2)

    self.assertNotEqual(s1, s2)

  def test_get_session(self):
    """ Test the get_session function """
    mediawikiapi.config.new_session()
    s1 = mediawikiapi.config.get_session()
    self.assertIsNotNone(s1)

    s2 = mediawikiapi.config.get_session()
    self.assertIsNotNone(s2)
    self.assertEqual(s1, s2)