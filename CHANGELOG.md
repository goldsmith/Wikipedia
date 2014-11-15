# Changelog

## Current

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
