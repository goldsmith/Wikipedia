.. _quickstart:

Quickstart
==========

These examples describe the unreleased 1.5.0 candidate and require Python 3.10
or newer. In a virtual environment, run ``python -m pip install .`` from a
checkout of this branch. The latest published PyPI release, 1.4.0, does not
include the new APIs or behavior described here.

.. code-block:: python

   import wikipedia

   wikipedia.set_user_agent("MyApplication/1.0 (https://example.org/contact)")
   wikipedia.set_timeout((5, 15))
   wikipedia.set_lang("en")
   titles = wikipedia.search("Earth", results=3)
   earth = wikipedia.page("Earth")
   print(earth.title, earth.url)
   print(earth.summary)
   print(earth.sections)

Replace the example URL with your application's contact page. Article contents,
search rankings, and available sections change over time.

Exact titles are tried first. Suggestions are a fallback when the title is absent;
use ``auto_suggest=False`` to disable this. Redirects are allowed by default;
``redirect=False`` raises ``RedirectError`` when Wikipedia reports a redirect.
Disambiguation pages raise ``DisambiguationError`` with candidate article titles
in ``error.options``. Missing pages raise ``PageError``.

Change language with ``wikipedia.set_lang("fr")`` and then use a title in that
language, such as ``wikipedia.summary("Terre")``. Existing page objects retain
their original language. Module configuration is global and should not be changed
concurrently with requests.

Requests have separate connection/read timeouts, not an overall operation deadline.
Catch ``HTTPTimeoutError`` for exhausted timeouts or ``RequestError`` for other HTTP,
API or malformed-response failures. ``RequestError.status_code``, ``api_code`` and
``retry_after`` contain details when available. ``set_timeout(None)`` explicitly
disables timeouts; use it only when unbounded waits are intended.

See :ref:`api` for functions, properties and exceptions.
