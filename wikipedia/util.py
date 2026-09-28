from __future__ import print_function, unicode_literals

import sys
import functools
import inspect
import time
from collections import OrderedDict
from copy import deepcopy
from threading import RLock

def debug(fn):
  def wrapper(*args, **kwargs):
    print(fn.__name__, 'called!')
    print(sorted(args), tuple(sorted(kwargs.items())))
    res = fn(*args, **kwargs)
    print(res)
    return res
  return wrapper


class cache(object):

  def __init__(self, fn):
    self.fn = fn
    self._cache = OrderedDict()
    self._signature = inspect.signature(fn)
    self._lock = RLock()
    functools.update_wrapper(self, fn)

  def __call__(self, *args, **kwargs):
    bound = self._signature.bind(*args, **kwargs)
    bound.apply_defaults()
    key = (self.fn.__globals__.get('API_URL'), tuple(bound.arguments.items()))
    try:
      hash(key)
    except TypeError:
      return self.fn(*args, **kwargs)
    with self._lock:
      entry = self._cache.get(key)
      if entry is not None:
        expires, value = entry
        if time.monotonic() < expires:
          self._cache.move_to_end(key)
          return deepcopy(value)
        del self._cache[key]
    value = self.fn(*args, **kwargs)
    with self._lock:
      self._cache[key] = (time.monotonic() + 300, deepcopy(value))
      self._cache.move_to_end(key)
      while len(self._cache) > 256:
        self._cache.popitem(last=False)
    return value

  def clear_cache(self):
    with self._lock:
      self._cache.clear()


def stdout_encode(u, default='UTF8'):
  """Return Unicode text; encoding belongs to the caller's output stream."""
  return u
