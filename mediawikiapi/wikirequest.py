import requests


class WikiRequest(object):
  """ Request wrapper class for request"""
  def __init__(self, config):
    """Require configuration instance as argument"""
    self.config = config
    self.__session = None

  def __del__(self):
    if self.session is not None:  
      self.session.close()

  @property
  def session(self):
    if self.__session is None:
      # initialize a session
      self.__session = requests.Session()
    return self.__session

  def new_session(self):
    self.__session = requests.Session()

  def request(self, params, language=None):
      '''
      Make a request to the Wikipedia API using the given search parameters.
      Returns a parsed dict of the JSON response.
      '''
      params['format'] = 'json'
      if not 'action' in params:
        params['action'] = 'query'

      headers = {
        'User-Agent': self.config.user_agent
      }

      rate_limit = self.config.rate_limit
      rate_limit_last_call = self.config.rate_limit_last_call
      
      if rate_limit_last_call and rate_limit_last_call + rate_limit > datetime.now():
        # it hasn't been long enough since the last API call
        # so wait until we're in the clear to make the request
        wait_time = (rate_limit_last_call + rate_limit) - datetime.now()
        time.sleep(int(wait_time.total_seconds()))
      r = self.session.get(self.config.get_api_url(language), params=params, headers=headers)

      if rate_limit:
        self.config.rate_limit_last_call = datetime.now()

      return r.json()
