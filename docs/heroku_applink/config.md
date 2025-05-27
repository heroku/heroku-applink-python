Module heroku_applink.config
============================

Classes
-------

<!-- python-config.md -->
# `Config`

```python
class Config(developer_name: str | None = None, attachment_or_url: str | None = None, request_timeout: float = 5, connect_timeout: float | None = None, socket_connect: float | None = None, socket_read: float | None = None)
```
Configuration for the Salesforce Data API client.

## Static methods

```python
def default() ‑> heroku_applink.config.Config
```

## Instance variables

* `attachment_or_url: str | None`
    The type of the None singleton.

* `connect_timeout: float | None`
    Timeout for connecting to the Salesforce Data API.

* `developer_name: str | None`
    The type of the None singleton.

* `request_timeout: float`
    Timeout for requests to the Salesforce Data API. In most cases, you'll only
    need to set this value. Connection Timeout, Socket Connect, and Socket Read
    are optional and only used in special cases.

* `socket_connect: float | None`
    Timeout for connecting to the Salesforce Data API.

* `socket_read: float | None`
    Timeout for reading from the Salesforce Data API.