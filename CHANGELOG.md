# Changelog

## Current

## Version 1.1

* Support python 2
* Add MediaWikiAPI and WikiRequest classes, now you can have more than one api access point with different configurations.
(Note! for compatibility with version 1 check [TODO ref_to_doc]
* Makes the pagepropsof a wikipedia page accessible [PR #147](https://github.com/goldsmith/Wikipedia/pull/147) from @goldsmith repo.
* Rename Configuration class to Config, add language field
* Config().get_api_url now accept language parameter
* Add timeout for requests, field in Config class called timeout (in seconds).
* Fix suggestion, issue [#108](https://github.com/goldsmith/Wikipedia/issues/108) by [PR #131](https://github.com/goldsmith/Wikipedia/pull/131) from @goldsmith repo.
* Fixed problem with hidden files in the article [PR #132](https://github.com/goldsmith/Wikipedia/pull/132/files) @goldsmith repo.
* DisambiguationError contains now information about title and url [PR #92](https://github.com/goldsmith/Wikipedia/pull/92) from @goldsmith repo.

All changes above are introduced in [PR #3](https://github.com/lehinevych/MediaWikiAPI/pull/3)

## Version 1

* Fork [Wikipedia](https://github.com/goldsmith/Wikipedia)
* Add language validation for mediawikiapi.set_lang
* Add lang title method to WikipediaPage
* Add re-usage the same requests session
* Fix installing error with version
* Fix WikipediaPage.sections
* Fix mock data
* Refactoring: seperate Language and Configuration classes
