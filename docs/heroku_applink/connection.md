Module heroku_applink.connection
================================

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