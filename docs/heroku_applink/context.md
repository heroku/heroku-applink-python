Module heroku_applink.context
=============================

Classes
-------

<!-- python-clientcontext.md -->
# `ClientContext`

```python
class ClientContext(*, org: heroku_applink.context.Org, data_api: heroku_applink.data_api.DataAPI, request_id: str, access_token: str, api_version: str, namespace: str)
```
Information about the Salesforce org that made the request.

## Static methods

```python
def from_header(header: str, connection: heroku_applink.connection.Connection)
```

## Instance variables

* `access_token: str`
    Valid access token for the current context org/user.

* `api_version: str`
    API version of the Salesforce component that made the request.

* `data_api: heroku_applink.data_api.DataAPI`
    An initialized data API client instance for interacting with data in the org.

* `namespace: str`
    Namespace of the Salesforce component that made the request.

* `org: heroku_applink.context.Org`
    Information about the Salesforce org and the user that made the request.

* `request_id: str`
    Request ID from the Salesforce org.

<!-- python-org.md -->
# `Org`

```python
class Org(*, id: str, domain_url: str, user: heroku_applink.context.User)
```
Information about the Salesforce org and the user that made the request.

## Instance variables

* `domain_url: str`
    The canonical URL of the Salesforce org.
    
    This URL never changes. Use this URL when making API calls to your org.
    
    For example: `https://example-domain-url.my.salesforce.com`

* `id: str`
    The Salesforce org ID.
    
    For example: `00DJS0000000123ABC`

* `user: heroku_applink.context.User`
    The currently logged in user.

<!-- python-user.md -->
# `User`

```python
class User(*, id: str, username: str)
```
Information about the Salesforce user that made the request.

## Instance variables

* `id: str`
    The user's ID.
    
    For example: `005JS000000H123`

* `username: str`
    The username of the user.
    
    For example: `user@example.tld`