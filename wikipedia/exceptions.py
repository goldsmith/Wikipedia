"""
Global wikipedia exception and warning classes.
"""

from typing import List, Union

ODD_ERROR_MESSAGE = (
    "This shouldn't happen. Please report on GitHub: github.com/goldsmith/Wikipedia"
)


class WikipediaException(Exception):
    """Base Wikipedia exception class."""

    def __init__(self, error: str):
        self.error = error

    def __unicode__(self):
        return f'An unknown error occured: "{self.error}". Please report it on GitHub!'

    def __str__(self):
        return self.__unicode__()


class PageError(WikipediaException):
    """Exception raised when no Wikipedia matched a query."""

    def __init__(self, pageid: Union[int, None] = None, *args: List[str]):
        if pageid:
            self.pageid = pageid
        else:
            self.title = args[0]

    def __unicode__(self):
        if hasattr(self, "title"):
            return f'"{self.title}" does not match any pages. Try another query!'
        else:
            return f'Page id "{self.pageid}" does not match any pages. Try another id!'


class DisambiguationError(WikipediaException):
    """
    Exception raised when a page resolves to a Disambiguation page.

    The `options` property contains a list of titles
    of Wikipedia pages that the query may refer to.

    .. note:: `options` does not include titles that do not link to a valid Wikipedia page.
    """

    def __init__(self, title: str, may_refer_to: List[str]):
        self.title = title
        self.options = may_refer_to

    def __unicode__(self):
        options = "\n".join(self.options)
        return f'"{self.title}" may refer to: \n{options}'


class RedirectError(WikipediaException):
    """Exception raised when a page title unexpectedly resolves to a redirect."""

    def __init__(self, title: str):
        self.title = title

    def __unicode__(self):
        return f'"{self.title}" resulted in a redirect. Set the redirect property to True to allow automatic redirects.'


class HTTPTimeoutError(WikipediaException):
    """Exception raised when a request to the Mediawiki servers times out."""

    def __init__(self, query: str):
        self.query = query

    def __unicode__(self):
        return f'Searching for "{self.query}" resulted in a timeout. Try again in a few seconds, and make sure you have rate limiting set to True.'
