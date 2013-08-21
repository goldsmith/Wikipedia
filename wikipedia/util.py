def debug(fn):
	def wrapper(*args, **kwargs):
		print fn.__name__, "called with args:", args.__str__(), "\nand kwargs:\n", '\n'.join("%s: %s" % (k, v) for k, v in kwargs.iteritems())
		res = fn(*args, **kwargs)
		print "\nreturning:", res, "\n\n"
		return res
	return wrapper