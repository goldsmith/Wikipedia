from datetime import timedelta
from .util import Singleton


class Configuration():
  # in Python3 metaclass=Singleton
  # For the compatibility with Python 2  
  __metaclass__ = Singleton
  DEFAULT_LANGUAGE='en'
  DEFAULT_USER_AGENT = 'mediawikiapi (https://github.com/lehinevych/MediaWikiAPI/)'
  API_URL = 'https://{}.wikipedia.org/w/api.php'
  DONATE_URL = 'https://donate.wikimedia.org/w/index.php?title=Special:FundraiserLandingPage'
  
  def __init__(self, lang=None, user_agent=None):
    self.lang = lang or self.DEFAULT_LANGUAGE
    self.api_url = self.API_URL.format(self.lang)
    self.user_agent = user_agent or self.DEFAULT_USER_AGENT
    self.rate_limit = False
    self.rate_limit_min_wait = None
    self.rate_limit_last_call = None

  def get_api_url(self):
    return self.api_url

  def get_user_agent(self):
    return self.user_agent

  def get_donate_url(self):
    return self.DONATE_URL

  def get_rate_limit(self):
    return self.rate_limit

  def get_rate_limit_min_wait(self):
    return self.rate_limit_min_wait

  def get_rate_limit_last_call(self):
    return self.rate_limit_last_call

  def set_lang(self, prefix):
    '''
    Change the language of the API being requested.
    Set `prefix` to one of the two letter prefixes found on the `list of all Wikipedias <http://meta.wikimedia.org/wiki/List_of_Wikipedias>`_.

    After setting the language, the cache for ``search``, ``suggest``, and ``summary`` will be cleared.
    .. note:: Make sure you search for page titles in the language that you have set.
    '''
    self.lang = prefix
    self.api_url = self.API_URL.format(self.lang)

  def set_user_agent(self, user_agent_string):
    '''
    Set the User-Agent string to be used for all requests.
    Arguments:
    * user_agent_string - (string) a string specifying the User-Agent header
    '''
    self.user_agent = user_agent_string

  def set_rate_limiting(self, rate_limit, min_wait=timedelta(milliseconds=50)):
    '''
    Enable or disable rate limiting on requests to the Mediawiki servers.
    If rate limiting is not enabled, under some circumstances (depending on
    load on Wikipedia, the number of requests you and other `wikipedia` users
    are making, and other factors), Wikipedia may return an HTTP timeout error.

    Enabling rate limiting generally prevents that issue, but please note that
    HTTPTimeoutError still might be raised.

    Arguments:
    * rate_limit - (Boolean) whether to enable rate limiting or not

    Keyword arguments:
    * min_wait - if rate limiting is enabled, `min_wait` is a timedelta describing the minimum time to wait before requests.
           Defaults to timedelta(milliseconds=50)
    '''
    self.rate_limit = rate_limit
    if not rate_limit:
      self.rate_limit_min_wait = None
    else:
      self.rate_limit_min_wait = min_wait

    self.rate_limit_last_call = None
