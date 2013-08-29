import functools


def debug(fn):
    def wrapper(*args, **kwargs):
        print fn.__name__, "called with args:\n", str(args) + str(kwargs), "\n"
        res = fn(*args, **kwargs)
        print "\nreturning:", res, "\n\n"
        return res
    return wrapper


def cache(fn):

    _cache = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in _cache:
            ret = _cache[key]
        else:
            ret = _cache[key] = fn(*args, **kwargs)

        return ret

    return wrapper
