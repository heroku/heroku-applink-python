Module heroku_applink
=====================

Sub-modules
-----------

* heroku_applink.config
* heroku_applink.connection
* heroku_applink.context
* heroku_applink.data_api
* heroku_applink.exceptions
* heroku_applink.middleware

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

<!-- python-clienterror.md -->
# `ClientError`

```python
class ClientError(*args, **kwargs)
```
Raised when there is an error with the HTTP client.

<!-- python-config.md -->
# `Config`

```python
class Config(request_timeout: float = 5, connect_timeout: float | None = None, socket_connect: float | None = None, socket_read: float | None = None)
```
Configuration for the Salesforce Data API client.

## Static methods

```python
def default() ‑> heroku_applink.config.Config
```

## Instance variables

* `connect_timeout: float | None`
    Timeout for connecting to the Salesforce Data API.

* `request_timeout: float`
    Timeout for requests to the Salesforce Data API. In most cases, you'll only
    need to set this value. Connection Timeout, Socket Connect, and Socket Read
    are optional and only used in special cases.

* `socket_connect: float | None`
    Timeout for connecting to the Salesforce Data API.

* `socket_read: float | None`
    Timeout for reading from the Salesforce Data API.

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
def request(self, method, url, headers=None, data=None, timeout: float | None = None) ‑> aiohttp.client_reqrep.ClientResponse
```
Make an HTTP request to the given URL.

If a timeout is provided, it will be used to set the timeout for the request.

<!-- python-integrationasgimiddleware.md -->
# `IntegrationAsgiMiddleware`

```python
class IntegrationAsgiMiddleware(app, config=Config(request_timeout=5, connect_timeout=None, socket_connect=None, socket_read=None))
```

<!-- python-integrationwsgimiddleware.md -->
# `IntegrationWsgiMiddleware`

```python
class IntegrationWsgiMiddleware(get_response, config=Config(request_timeout=5, connect_timeout=None, socket_connect=None, socket_read=None))
```

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

<!-- python-queriedrecord.md -->
# `QueriedRecord`

```python
class QueriedRecord(*, type: str, fields: dict[str, typing.Any], sub_query_results: dict[str, 'RecordQueryResult'] = <factory>)
```
A Salesforce record that's the result of a SOQL query.

Extends `Record` with potential sub query results that can only exist when
a record was queried from the data API.

## Instance variables

* `sub_query_results: dict[str, heroku_applink.data_api.record.RecordQueryResult]`
    Additional query results from sub queries.

<!-- python-record.md -->
# `Record`

```python
class Record(*, type: str, fields: dict[str, typing.Any])
```
A Salesforce record.

A record describes a particular occurrence of a Salesforce object, such as a
specific account "Acme Company" from the Account standard object. A record is
analogous to a row in a database table.

## Instance variables

* `fields: dict[str, typing.Any]`
    The fields belonging to the record.

* `type: str`
    The Salesforce Object type.
    
    For example: `Account`

<!-- python-recordqueryresult.md -->
# `RecordQueryResult`

```python
class RecordQueryResult(*, done: bool, total_size: int, records: list[heroku_applink.data_api.record.QueriedRecord], next_records_url: str | None)
```
The result of a record query.

## Instance variables

* `done: bool`
    Indicates whether all record results have been returned.
    
    If true, no additional records can be retrieved from the query result.
    If false, one or more records remain to be retrieved.

* `next_records_url: str | None`
    The URL for the next set of records, if any.

* `records: list[heroku_applink.data_api.record.QueriedRecord]`
    The list of `Record`s in this query result.
    
    Use `done` to determine whether there are additional records to be
    queried with `queryMore`.

* `total_size: int`
    The total number of records returned by the query.
    
    This number isn't necessarily the same as the number of records found in `records`.

<!-- python-referenceid.md -->
# `ReferenceId`

```python
class ReferenceId(*, id: str)
```
A reference ID for an operation inside a `UnitOfWork`.

Used to reference results of other operations inside the same unit of work.

## Instance variables

* `id: str`
    The internal identifier of this `ReferenceId`.

<!-- python-unexpectedrestapiresponsepayload.md -->
# `UnexpectedRestApiResponsePayload`

```python
class UnexpectedRestApiResponsePayload(*args, **kwargs)
```
Raised when the API response is not in the expected format.

<!-- python-unitofwork.md -->
# `UnitOfWork`

```python
class UnitOfWork()
```
Represents a `UnitOfWork`.

A `UnitOfWork` encapsulates a set of one or more Salesforce operations that must be
performed as a single atomic operation. Single atomic operations reduce the number of
requests back to the org, and are more efficient when working with larger data volumes.

First, register the create, update, or delete operations that make up the `UnitOfWork`
using their corresponding methods, such as `register_create`. Then submit the `UnitOfWork`
with the `commit_unit_of_work` method of `DataAPI`.

For example:

```python
# Create a unit of work, against which multiple operations can be registered.
unit_of_work = UnitOfWork()

# Register a new Account for creation
account_reference_id = unit_of_work.register_create(
    Record(
        type="Account",
        fields={
            "Name": "Example Account",
        },
    )
)

# Register a new Contact for creation, that references the account above.
unit_of_work.register_create(
    Record(
        type="Contact",
        fields={
            "FirstName": "Joe",
            "LastName": "Smith",
            "AccountId": account_reference_id,
        },
    )
)

# Commit the unit of work, executing all of the operations registered above.
result = await context.org.data_api.commit_unit_of_work(unit_of_work)
```

## Methods

### `register_create`

```python
def register_create(self, record: heroku_applink.data_api.record.Record) ‑> heroku_applink.data_api.reference_id.ReferenceId
```
Register a record creation for the `UnitOfWork`.

Returns a `ReferenceId` that you can use to refer to the created record in subsequent operations in this
`UnitOfWork`.

For example:

```python
unit_of_work = UnitOfWork()

reference_id = unit_of_work.register_create(
    Record(
        type="Account",
        fields={
            "Name": "Example Account",
        },
    )
)
```

### `register_delete`

```python
def register_delete(self, object_type: str, record_id: str) ‑> heroku_applink.data_api.reference_id.ReferenceId
```
Register a deletion of an existing record of the given type and ID.

Returns a `ReferenceId` that you can use to refer to the deleted record in subsequent operations in this
`UnitOfWork`.

For example:

```python
unit_of_work = UnitOfWork()

reference_id = unit_of_work.register_delete("Account", "001B000001Lp1FxIAJ")
```

### `register_update`

```python
def register_update(self, record: heroku_applink.data_api.record.Record) ‑> heroku_applink.data_api.reference_id.ReferenceId
```
Register a record update for the `UnitOfWork`.

The given `Record` must contain an `Id` field.

Returns a `ReferenceId` that you can use to refer to the updated record in subsequent operations in this
`UnitOfWork`.

For example:

```python
unit_of_work = UnitOfWork()

reference_id = unit_of_work.register_update(
    Record(
        type="Account",
        fields={
            "Id": "001B000001Lp1FxIAJ",
            "Name": "New Name",
        },
    )
)
```

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