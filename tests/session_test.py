# -*- coding: utf-8 -*-
import unittest

import wikipedia

class TestSession(unittest.TestCase):
  def test_session(self):
    """ Test the new_session function """
    wikipedia.new_session()
    s1 = wikipedia.get_session()
    wikipedia.new_session()
    s2 = wikipedia.get_session()

    self.assertNotEqual(s1, s2)
