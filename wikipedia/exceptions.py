"""
Global wikipedia excpetion and warning classes.
"""

import sys

class WikipediaException(Exception):
    """Base Wikipedia exception class."""

    if sys.version_info > (3, 0):
        def __str__(self):
            return self.__unicode__()

    else:
        def __str__(self):
            return self.__unicode__().encode('utf8')


class PageError(WikipediaException):
    """Exception raised when no Wikipedia matched a query."""

    def __init__(self, page_title):
        self.title = page_title

    def __unicode__(self):
        return u"\"{0}\" does not match any pages. Try another query!".format(self.title)


class DisambiguationError(WikipediaException):
    """
    Exception raised when a page resolves to a Disambiguation page.

    The `options` property contains a list of titles
    of Wikipedia pages that the query may refer to.

    .. note:: `options` does not include titles that do not link to a valid Wikipedia page.
    """

    def __init__(self, title, may_refer_to):
        self.title = title
        self.options = may_refer_to

    def __unicode__(self):
        return u"\"{0}\" may refer to: \n{1}".format(self.title, '\n'.join(self.options))


class RedirectError(WikipediaException):
    """Exception raised when a page title unexpectedly resolves to a redirect."""

    def __init__(self, page_title):
        self.title = page_title

    def __unicode__(self):
        return u"\"{0}\" resulted in a redirect. Set the redirect property to True to allow automatic redirects.".format(self.title)
