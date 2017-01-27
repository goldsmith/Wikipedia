import requests
from datetime import datetime
from .config import Configuration
from .language import Language
from .util import Singleton


class WikiRequest(object):
  """
  Contain general mediawiki api queries
  Only for internal usage
  """
  # in Python3 metaclass=Singleton
  # For the compatibility with Python 2  
  __metaclass__ = Singleton
 
  def __init__(self):
    self.config = Configuration(lang=Language())
    self.session = None

  def __del__(self):
    if self.session is not None:  
      self.session.close()

  def set_lang(lang):
    self.config.set_lang(prefix=lang)

  def get_session(self):
    if self.session is None:
      # initialize a session
      self.session = requests.Session()
    return self.session

  def new_session(self):
    self.session = requests.Session()

  def request(self, params):
    '''
    Make a request to the Wikipedia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''
    params['format'] = 'json'
    if not 'action' in params:
      params['action'] = 'query'

    headers = {
      'User-Agent': self.config.get_user_agent()
    }

    rate_limit = self.config.get_rate_limit()
    rate_limit_last_call = self.config.get_rate_limit_last_call()
    rate_limit_min_wait = self.config.get_rate_limit_min_wait()
    if rate_limit and rate_limit_last_call and \
      rate_limit_last_call + rate_limit_min_wait > datetime.now():

      # it hasn't been long enough since the last API call
      # so wait until we're in the clear to make the request

      wait_time = (rate_limit_last_call + rate_limit_min_wait) - datetime.now()
      time.sleep(int(wait_time.total_seconds()))
   
    r = self.get_session().get(self.config.get_api_url(), params=params, headers=headers)

    if rate_limit:
      rate_limit_last_call = datetime.now()

    return r.json()

  def languages(self):
    '''
    List all the currently supported language prefixes (usually ISO language code).

    Can be inputted to `set_lang` to change the Mediawiki that `wikipedia` requests
    results from.

    Returns: dict of <prefix>: <local_lang_name> pairs. To get just a list of prefixes,
    use `wikipedia.languages().keys()`.
    '''
    response = self.request({
      'meta': 'siteinfo',
      'siprop': 'languages'
    })
    languages = response['query']['languages']
    return {
      lang['code']: lang['*']
      for lang in languages
    }