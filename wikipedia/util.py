import functools
import sys
from typing import Any, Callable, Dict, List


def debug(fn: Callable[[Any], Any]):
    """Print the function call and return value"""

    def wrapper(*args: List[Any], **kwargs: Dict[Any, Any]):
        print(fn.__name__, "called!")
        print(sorted(args), tuple(sorted(kwargs.items())))
        res = fn(*args, **kwargs)
        print(res)
        return res

    return wrapper


class cache(object):
    """Cache the results of a function call"""

    def __init__(self, fn: Callable[[Any], Any]):
        self.fn = fn
        self._cache: Dict[Any, Any] = {}
        functools.update_wrapper(self, fn)

    def __call__(self, *args: List[Any], **kwargs: Dict[Any, Any]):
        key = str(args) + str(kwargs)
        ret = self._cache.get(key, self.fn(*args, **kwargs))
        self._cache[key] = ret
        return ret

    def clear_cache(self):
        self._cache = {}


# from http://stackoverflow.com/questions/3627793/best-output-type-and-encoding-practices-for-repr-functions
def stdout_encode(u: str, default: str = "utf-8") -> str:
    encoding = sys.stdout.encoding or default
    return u.encode(encoding, errors="replace").decode(encoding)
