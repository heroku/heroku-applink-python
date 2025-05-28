Module heroku_applink.authorization
===================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

Classes
-------

<!-- python-authbundle.md -->
# `AuthBundle`

```python
class AuthBundle(api_url: str, token: str)
```
A bundle of authentication information for the Salesforce Data API. This
class should not leak outside of the Authorization class.

## Instance variables

* `api_url: str`
    The type of the None singleton.

* `token: str`
    The type of the None singleton.

<!-- python-authorization.md -->
# `Authorization`

```python
class Authorization(config: heroku_applink.config.Config)
```

## Methods

### `get_client_context`

```python
def get_client_context(self) ‑> heroku_applink.context.ClientContext
```
Fetch authorization for a given Heroku AppLink developer.
Uses GET {apiUrl}/authorizations/{developer_name}
with a Bearer token from the add-on config.

For a list of exceptions, see:
  * https://docs.aiohttp.org/en/stable/client_reference.html