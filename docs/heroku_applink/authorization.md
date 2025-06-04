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
class AuthBundle(*, api_url: str, token: str)
```
A bundle of authentication information for the Salesforce Data API. This
class should not leak outside of the Authorization class.

## Instance variables

* `api_url: str`
    

* `token: str`
    

<!-- python-authorization.md -->
# `Authorization`

```python
class Authorization(connection: heroku_applink.connection.Connection, data_api: heroku_applink.data_api.DataAPI, id: str, status: str, org: heroku_applink.authorization.Org, created_at: datetime.datetime, created_by: str, created_via_app: str | None, last_modified_at: datetime.datetime, last_modified_by: str | None, redirect_uri: str | None)
```
Authorization information for a Salesforce org with access to a Data API for
making SOQL queries.

## Static methods

```python
def find(developer_name: str, attachment_or_url: str | None = None, config: heroku_applink.config.Config = Config(request_timeout=5, connect_timeout=None, socket_connect=None, socket_read=None)) ‑> heroku_applink.authorization.Authorization
```
Fetch authorization for a given Heroku AppLink developer.
Uses GET {apiUrl}/authorizations/{developer_name}
with a Bearer token from the add-on config.

This function will raise aiohttp-specific exceptions for HTTP errors and
any HTTP response other than 200 OK.

For a list of exceptions, see:
* https://docs.aiohttp.org/en/stable/client_reference.html

## Instance variables

* `connection: heroku_applink.connection.Connection`
    Object responsible for making HTTP requests to the Salesforce API.

* `created_at: datetime.datetime`
    The date and time the authorization was created.
    
    For example: `2025-03-06T18:20:42.226577Z`

* `created_by: str`
    The user who created the authorization.
    
    For example: `user@example.tld`

* `created_via_app: str | None`
    The app that created the authorization.
    
    For example: `sushi`

* `data_api: heroku_applink.data_api.DataAPI`
    An initialized data API client instance for interacting with data in the org.
    
    Example usage:
    
    ```python
    authorization = await Authorization.find(developer_name)
    result = await authorization.data_api.query("SELECT Id, Name FROM Account")
    
    for record in result.records:
        print(f"Account: {record}")
    ```

* `id: str`
    The ID of the authorization in UUID format.
    
    For example: `e27e9be0-6dc4-430f-974d-584f5ff8e9e6`

* `last_modified_at: datetime.datetime`
    The date and time the authorization was last modified.
    
    For example: `2025-03-06T18:20:42.226577Z`

* `last_modified_by: str | None`
    The user who last modified the authorization.
    
    For example: `user@example.tld`

* `org: heroku_applink.authorization.Org`
    The Salesforce Org associated with the authorization.

* `redirect_uri: str | None`
    The redirect URI for the authorization.

* `status: str`
    The status of the authorization.
    
    Possible values:
    * "authorized"
    * "authorizing"
    * "disconnected"
    * "error"

<!-- python-org.md -->
# `Org`

```python
class Org(*, id: str, developer_name: str, instance_url: str, type: str, api_version: str, user_auth: heroku_applink.authorization.UserAuth)
```
Salesforce org information.

## Instance variables

* `api_version: str`
    

* `developer_name: str`
    

* `id: str`
    

* `instance_url: str`
    

* `type: str`
    

* `user_auth: heroku_applink.authorization.UserAuth`
    

<!-- python-userauth.md -->
# `UserAuth`

```python
class UserAuth(*, username: str, user_id: str, access_token: str)
```
User authentication information for the Salesforce org.

## Instance variables

* `access_token: str`
    

* `user_id: str`
    

* `username: str`