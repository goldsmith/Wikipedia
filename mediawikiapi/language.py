import requests
from .exceptions import LanguageError


class Language(object):
  '''
  Wrapper over language used in mediawiki
  If language is not defined, use English
  The verification stage is available only in case we will set predefined_languages
  Verify the language, if language doesn't exists get LanguageError exception
  '''
  DEFAULT_LANGUAGE='en'
  
  def __init__(self, lang=None):
    params = {
      'meta': 'siteinfo',
      'siprop': 'languages',
      'format': 'json',
      'action': 'query',
    }
    headers = {
      'User-Agent': 'mediawikiapi (https://github.com/lehinevych/MediaWikiAPI/)'
    }
    response = requests.get('https://en.wikipedia.org/w/api.php', params=params, headers=headers)
    response = response.json()
    languages = response['query']['languages']
    self.predefined_languages ={
      lang['code']: lang['*'] for lang in languages
    }
    if lang is None:
      self.lang = self.DEFAULT_LANGUAGE

    elif self._verify_lang(lang):
      self.lang = lang
    else:
      raise LanguageError(lang)

  def get_lang(self):
    return self.lang

  def set_lang(self, lang):
    '''
    Verify language
    Raise LanguageError if such doesn't exist 
    '''
    lang=lang.lower()
    if lang in self.predefined_languages.keys():
      self.lang = lang
    else:
      raise LanguageError(lang)

  def _verify_lang(self, lang):
    return lang in self.predefined_languages.keys()

