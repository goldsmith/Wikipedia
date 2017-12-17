import requests
from datetime import timedelta
from .language import Language


class Config():
  """
  Contains global configuration
  """
  DEFAULT_USER_AGENT = 'mediawikiapi (https://github.com/lehinevych/MediaWikiAPI/)'
  DONATE_URL = 'https://donate.wikimedia.org/w/index.php?title=Special:FundraiserLandingPage'
  API_URL = 'https://{}.wikipedia.org/w/api.php'

  def __init__(self, language=None, user_agent=None, rate_limit=None):
    if language is not None:
      self.__lang = Language(language)
    else:
      self.__lang = Language()
    self.__rate_limit_last_call = None
    self.__rate_limit = rate_limit
    self.timeout = None
    self.user_agent = user_agent or self.DEFAULT_USER_AGENT


  @property
  def donate_url(self):
    '''Return media wiki donate url'''
    return self.DONATE_URL

  @property
  def language(self):
    '''Return current global language'''
    return self.__lang.language

  @language.setter
  def language(self, language):
    '''Set a new language
    Arguments:
    * language - (string or Language instance) specifying the language
    '''
    if isinstance(language, Language):
      self.__lang=language
    else:
      self.__lang.language = language

  def get_api_url(self, language=None):
    '''Return api for specified language
    Arguments:
    * language - (string or Language instance) specifying the language
    '''
    if language is not None:
      if isinstance(language, Language):
        return self.API_URL.format(language.language)
      else:
        # does the language verification
        lang = Language(language)
        return self.API_URL.format(lang.language)
    return self.API_URL.format(self.__lang.language)
    
  @property
  def rate_limit(self):
    return self.__rate_limit

  @property
  def rate_limit_last_call(self):
    return self.__rate_limit_last_call

  @rate_limit_last_call.setter
  def rate_limit_last_call(self, last_call):
    self.__rate_limit_last_call = last_call

  @rate_limit.setter
  def rate_limit(self, rate_limit):
    '''
    Enable or disable rate limiting on requests to the Mediawiki servers.
    If rate limiting is not enabled, under some circumstances (depending on
    load on Wikipedia, the number of requests you and other `wikipedia` users
    are making, and other factors), Wikipedia may return an HTTP timeout error.

    Enabling rate limiting generally prevents that issue, but please note that
    HTTPTimeoutError still might be raised.

    Arguments:
    * min_wait - (integer or timedelta) describes the minimum time to wait in miliseconds before requests.
           Example timedelta(milliseconds=50). If None, rate_limit won't be used.

    '''
    if rate_limit is None:
      self.__rate_limit = None
    elif isinstance(rate_limit, timedelta):
      self.__rate_limit = rate_limit
    else: 
      self.__rate_limit = timedelta(milliseconds=rate_limit)
    
    self.__rate_limit_last_call = None
