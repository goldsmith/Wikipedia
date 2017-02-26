# -*- coding: utf-8 -*-
import unittest

from mediawikiapi import MediaWikiAPI
api = MediaWikiAPI()


class TestSession(unittest.TestCase):
  
  def test_new_session(self):
    """ Test the new_session function """
    api.wiki_request.new_session()
    s1 = api.wiki_request.session
    self.assertIsNotNone(s1)

    api.wiki_request.new_session()
    s2 = api.wiki_request.session
    self.assertIsNotNone(s2)

    self.assertNotEqual(s1, s2)

  def test_get_session(self):
    """ Test the get_session function """
    api.wiki_request.new_session()
    s1 = api.wiki_request.session
    self.assertIsNotNone(s1)

    s2 = api.wiki_request.session
    self.assertIsNotNone(s2)
    self.assertEqual(s1, s2)