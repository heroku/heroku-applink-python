Module heroku_applink.connection
================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

Functions
---------

<!-- python-get_request_id.md -->
# `get_request_id`

```python
def get_request_id() ‑> str
```
Get the request ID for the current request.

<!-- python-set_request_id.md -->
# `set_request_id`

```python
def set_request_id(new_request_id: str)
```
Set the request ID for the current request.

Classes
-------

<!-- python-connection.md -->
# `Connection`

```python
class Connection(config: heroku_applink.config.Config)
```
A connection for making asynchronous HTTP requests.

## Methods

### `close`

```python
def close(self)
```
Close the connection.

### `request`

```python
def request(self, method, url, params=None, headers=None, data=None, timeout: float | None = None) ‑> aiohttp.client_reqrep.ClientResponse
```
Make an HTTP request to the given URL.

If a timeout is provided, it will be used to set the timeout for the request.