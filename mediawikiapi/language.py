import requests
from .exceptions import LanguageError

def __get_available_languages():
  '''
    Internal static function for getting all available language on mediawiki
  '''
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
  return {lang['code']: lang['*'] for lang in languages}


predefined_languages = __get_available_languages()


class Language(object):
  '''
  Wrapper over language used in mediawiki
  If language is not defined, use English
  The verification stage is available only in case we will set predefined_languages
  Verify the language, if language doesn't exists get LanguageError exception
  '''
  DEFAULT_LANGUAGE='en'
  
  def __init__(self, language=None):
    if language is None:
      self.language = self.DEFAULT_LANGUAGE
    else:
      self.language = language

  @property
  def language(self):
    '''
    Return language
    '''
    return self._language

  @language.setter
  def language(self, language):
    '''
    Change the language of the API being requested.
    Set `language` to one of the two letter prefixes found on the
    `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.
    Raise error if language not in a list of predefined languages
    Args:
    * language - (string) a string specifying the language
    '''
    language=language.lower()
    if language in predefined_languages.keys():
      self._language = language
    else:
      raise LanguageError(language)



