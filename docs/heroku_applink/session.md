Module heroku_applink.session
=============================

Classes
-------

<!-- python-session.md -->
# `Session`

```python
class Session(config: heroku_applink.config.Config)
```

## Methods

### `client`

```python
def client(self) ‑> aiohttp.client.ClientSession
```

### `close`

```python
def close(self)
```

### `request`

```python
def request(self, method, url, headers=None, data=None)
```