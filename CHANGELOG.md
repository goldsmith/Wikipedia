# Changes

## 1.5.0 — 2026-10-24

- Require Python 3.10 or newer; test through 3.14. Modern build metadata, wheels,
  offline pytest coverage and GitHub Actions replace the obsolete Travis setup.
- Resolve exact titles before a single suggestion fallback, preserving the
  `auto_suggest=True` default and public positional signatures. Exact disambiguation
  pages raise rather than silently resolving to an unrelated article.
- Use HTTPS, connection reuse and configurable timeouts (default connect 5s/read
  15s). Add `set_timeout` and `RequestError`. Retry transient failures at most twice,
  honor Retry-After within a 30-second retry-sleep budget, and fix fractional rate limits.
  Timeouts are inactivity limits, not a total deadline for a multi-request operation.
- Preserve page objects' originating language; invalidate geosearch on language changes.
  Module caches expire after five minutes and hold at most 256 entries each. Cached
  mutable outputs and list page properties are returned defensively.
- Fix page-ID redirects and missing-title exception attributes. Empty PageError
  construction no longer crashes. Existing exception class names remain available.
- Return empty lists for absent list properties and None for absent coordinates;
  cache empty results. Reject malformed response structures and repeated continuation
  tokens; raise on mid-pagination failures instead of returning partial results.
- Use supported parse requests for HTML and table-of-contents data; a null TOC
  correctly returns an empty sections list. Disambiguation
  options are unique existing article targets rather than potentially misleading labels.
- Match section headings as complete lines, retaining the existing exclusion of
  subsection content. Decode section heading markup. Strip localized category namespaces.
- Make Unicode page representations independent of terminal encoding.
- Keep absolute external-link schemes intact; protocol-relative references become HTTPS.
- Retain tuple `__version__`, Decimal coordinates, random return shapes, and the
  existing meanings of links, images, references, text extracts and lazy properties.
- Incorporate PR #351 with original authorship: object equality no longer swallows
  KeyboardInterrupt or SystemExit. See CONTRIBUTIONS.md for contributor acknowledgments.

## Version 1.4

* Test wikipdia library on Python v3.4. PR [#52](https://github.com/goldsmith/Wikipedia/pull/52) by [frewsxcv](https://github.com/frewsxcv)
* Add WikipediaPage.categories attribute. PR [#59](https://github.com/goldsmith/Wikipedia/pull/59) by [@willf](https://github.com/willf)

### Version 1.3.1

* Determine package version without importing ``wikipedia`` in setup.py. Fixes [#50](https://github.com/goldsmith/Wikipedia/issues/50) reported by [@arcolife](https://github.com/arcolife)

* Update ``requests`` dependency to v2.3.0

## Version 1.3

* wikipedia.languages() for easy access to all language prefixes
* Conditional check for normalization in redirect queries. Fixes [#47](https://github.com/goldsmith/Wikipedia/issues/47)
* Remove pip requirement to fix pip installation error. Fixes [#46](https://github.com/goldsmith/Wikipedia/issues/46#issuecomment-44221725) reported by [@oquidav](https://github.com/oquidave)

### Version 1.2.1

* Refactor query functions to standardize & fix functionality of WikipediaPage properties that return a list. Fixes [#38](https://github.com/goldsmith/Wikipedia/issues/38) reported by [@gwezerek](https://github.com/gwezerek)

* Use official Mediawiki API 'redirects' key to avoid redirection parse errors. Fixes [#28](https://github.com/goldsmith/Wikipedia/issues/28)
  reported by [@shichao-an](https://github.com/shichao-an) and [#32](https://github.com/goldsmith/Wikipedia/issues/32) reported by [@dmirylenka](https://github.com/dmirylenka)

## Version 1.2

* Add revision_id and parent_id properties. PR [#23](https://github.com/goldsmith/Wikipedia/pull/23) by [@fusiongyro](https://github.com/fusiongyro)
* Add changeable User-Agent. PR [#33](https://github.com/goldsmith/Wikipedia/pull/33) by [@crazybmanp](https://github.com/crazybmanp)
* Add geosearch functionality. PR [#40](https://github.com/goldsmith/Wikipedia/pull/40) by [@Kazuar](https://github.com/Kazuar)

## Version 1.1

* Add limited ability to access section titles on a page.  PR [#18](https://github.com/goldsmith/Wikipedia/pull/18) by [@astavonin](https://github.com/astavonin)
* Add optional rate limiting. Closes issue [#20](https://github.com/goldsmith/Wikipedia/pull/20) reported by [@mobeets](https://github.com/mobeets)
* Add HTTPTimeout exception

### Version 1.0.2

* Fix installation issue on some Python 3 machines. Closes issue [#15](https://github.com/goldsmith/Wikipedia/issues/15) by [@wronglink](https://github.com/wronglink)
* Add Python 3 support on PyPI

## Version 1.0

* Add international support
* Fix continue values with Mediawiki API
* Support Python 3

### Version 0.9

* Initial functionality
* Add documentation and upload to ReadTheDocs
