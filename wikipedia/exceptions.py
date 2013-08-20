"""
Global wikipedia excpetion and warning classes.
"""

class PageError(Exception):
	"""Exception raised when no Wikipedia matched a query."""

	def __init__(self, page_title):
		self.title = page_title

	def __str__(self):
		return "\"%s\" does not match any pages. Try another query!" % self.title

class DisambiguationError(Exception):
	"""
	Exception raised when a page resolves to a Disambiguation page.

	The `options` property contains a list of titles 
	of Wikipedia pages that the query may refer to.
	"""

	def __init__(self, title, may_refer_to):
		self.title = title
		self.options = may_refer_to

	def __str__(self):
		return "\"%s\" may refer to: \n%s" % (self.title, '\n'.join(self.options))

class RedirectError(Exception):
	"""Exception raised when a page title unexpectedly resolves to a redirect."""

	def __init__(self, page_title):
		self.title = page_title

	def __str__(self):
		return ("\"%s\" resulted in a redirect. Did you mean to enable the keyword argument `redirect`?" % self.title)

