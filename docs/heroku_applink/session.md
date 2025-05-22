Module heroku_applink.session
=============================

Classes
-------

<!-- python-session.md -->
# `Session`

```python
class Session(config: heroku_applink.config.Config)
```
A session for making asynchronous HTTP requests.

## Methods

### `close`

```python
def close(self)
```
Close the session.

### `request`

```python
def request(self, method, url, headers=None, data=None, timeout: float | None = None) ‑> aiohttp.client_reqrep.ClientResponse
```
Make an HTTP request to the given URL.

If a timeout is provided, it will be used to set the timeout for the request.