# -*- coding: utf-8 -*-
import unittest

import wikipedia

class TestSession(unittest.TestCase):
  def test_session(self):
    """ Test the new_session function """
    wikipedia.new_session()
    s1 = wikipedia.wikipedia.SESSION
    self.assertIsNotNone(s1)

    wikipedia.new_session()
    s2 = wikipedia.wikipedia.SESSION
    self.assertIsNotNone(s2)

    self.assertNotEqual(s1, s2)
