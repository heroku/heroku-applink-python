# Changelog

All notable changes to this project will be documented in this file.
See [Conventional Commits](https://conventionalcommits.org) for commit guidelines.

# [1.1.2](https://github.com/heroku/heroku-applink-python/compare/v1.0.0...1.1.2) - 2025-09-03


### Changes

* Errors from requests to the Salesforce REST API will now result in `SalesforceRestApiError` being raised, rather than `aiohttp.ClientResponseError`. (#82) ([#82](https://github.com/heroku/heroku-applink-python/pull/82)) -- this was from v1.1.0, which did not get released.


### Features


### Other

* attempt to add gpg key with passphrase too
* release-v1.1.1 bump-patch
*  add GPG key to enable signed tags (#84) ([#84](https://github.com/heroku/heroku-applink-python/pull/84))
* release-v1.1.0 bump-minor
* Don't use raise_for_status by default
* building instead of downloading artifact (#80) ([#80](https://github.com/heroku/heroku-applink-python/pull/80))

# [1.1.1](https://github.com/heroku/heroku-applink-python/compare/v1.0.0...1.1.1) - 2025-09-03


### Changes

* Errors from requests to the Salesforce REST API will now result in `SalesforceRestApiError` being raised, rather than `aiohttp.ClientResponseError`. (#82) ([#82](https://github.com/heroku/heroku-applink-python/pull/82)) -- this was from v1.1.0, which did not get released.

### Features


### Other

* Update CHANGELOG.md
*  add GPG key to enable signed tags (#84) ([#84](https://github.com/heroku/heroku-applink-python/pull/84))
* release-v1.1.0 bump-minor
* Don't use raise_for_status by default
* building instead of downloading artifact (#80) ([#80](https://github.com/heroku/heroku-applink-python/pull/80))

# [1.1.0](https://github.com/heroku/heroku-applink-python/compare/v1.0.0...1.1.0) - 2025-09-02


### Changes

* Errors from requests to the Salesforce REST API will now result in `SalesforceRestApiError` being raised, rather than `aiohttp.ClientResponseError`. (#82) ([#82](https://github.com/heroku/heroku-applink-python/pull/82))

### Other

* building instead of downloading artifact (#80) ([#80](https://github.com/heroku/heroku-applink-python/pull/80))

# [1.0.0](https://github.com/heroku/heroku-applink-python/compare/v0.2.0...1.0.0) - 2025-06-19


### Changes

* major release v1.0.0

### Other

# [0.2.0](https://github.com/heroku/heroku-applink-python/compare/TDX...0.2.0) - 2025-06-13


### Changes


### Features

* Adds Record.get so our example code will function (#60) ([#60](https://github.com/heroku/heroku-applink-python/pull/60))
* Updates getAuthorization to handle redirectURI missing (#51) ([#51](https://github.com/heroku/heroku-applink-python/pull/51))
* Implement get_authorization feature in Python SDK (#18) ([#18](https://github.com/heroku/heroku-applink-python/pull/18))
* Adding integration tests for ASGI/WSGI middlewares (#47) ([#47](https://github.com/heroku/heroku-applink-python/pull/47))
* Supporting configurable timeouts for HTTP requests (#46) ([#46](https://github.com/heroku/heroku-applink-python/pull/46))

### Fixes

* Fixing a bug that caused URL paths to be excluded (#58) ([#58](https://github.com/heroku/heroku-applink-python/pull/58))
*  add x-app-uuid to headers for auth requests

### Docs

### Other

* Optional namespace, convert byte for header (#74) ([#74](https://github.com/heroku/heroku-applink-python/pull/74))
* Include X-Request-Id header in all outbound requests (#63) ([#63](https://github.com/heroku/heroku-applink-python/pull/63))
* Testing on multiple OSes and only the specific version of Python (#72) ([#72](https://github.com/heroku/heroku-applink-python/pull/72))
* Gets the version via importlib.metadata to use as the user-agent (#73) ([#73](https://github.com/heroku/heroku-applink-python/pull/73))
* use hatchling (#49) ([#49](https://github.com/heroku/heroku-applink-python/pull/49))
* Making DataAPI a field on Authorization (#50) ([#50](https://github.com/heroku/heroku-applink-python/pull/50))
* Using uv for build/test/lint (#43) ([#43](https://github.com/heroku/heroku-applink-python/pull/43))

# [0.1.0](https://github.com/heroku/heroku-applink-python/compare/HEAD...0.1.0) - 2025-03-04


### Changes

### Features
* initial release ([c5d593f](https://github.com/heroku/heroku-applink-python/commit/c5d593fa3c0f37607239e3ded7c2c24d7354383c))

