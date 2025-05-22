Module heroku_applink.data_api
==============================

Sub-modules
-----------

* heroku_applink.data_api.exceptions
* heroku_applink.data_api.record
* heroku_applink.data_api.reference_id
* heroku_applink.data_api.unit_of_work

Classes
-------

<!-- python-dataapi.md -->
# `DataAPI`

```python
class DataAPI(*, org_domain_url: str, api_version: str, access_token: str, session: heroku_applink.session.Session)
```
Data API client to interact with data in a Salesforce org.

We provide a preconfigured instance of this client at `context.org.data_api`
to make it easier for you to query, insert, and update records.

## Methods

### `commit_unit_of_work`

```python
def commit_unit_of_work(self, unit_of_work: heroku_applink.data_api.unit_of_work.UnitOfWork) ‑> dict[heroku_applink.data_api.reference_id.ReferenceId, str]
```
Commit a `UnitOfWork`, which executes all operations registered with it.

If any of these operations fail, the whole unit is rolled back. To examine results for a
single operation, inspect the returned dict (which is keyed with `ReferenceId` objects
returned from the `register*` functions on `UnitOfWork`).

For example:

```python
# Create a unit of work, against which multiple operations can be registered.
unit_of_work = UnitOfWork()

first_reference_id = unit_of_work.register_create(
    # ...
)
second_reference_id = unit_of_work.register_create(
    # ...
)

# Commit the unit of work, executing all of the operations registered above.
result = await context.org.data_api.commit_unit_of_work(unit_of_work)

# The result of each operation.
first_record_id = result[first_create_reference_id]
second_record_id = result[second_create_reference_id]
```

### `create`

```python
def create(self, record: heroku_applink.data_api.record.Record) ‑> str
```
Create a new record based on the given `Record` object.

Returns the ID of the new record.

For example:

```python
record_id = await context.org.data_api.create(
    Record(
        type="Account",
        fields={
            "Name": "Example Account",
        },
    )
)
```

### `delete`

```python
def delete(self, object_type: str, record_id: str) ‑> str
```
Delete an existing record of the given Salesforce object type and ID.

Returns the ID of the record that was deleted.

For example:

```python
await data_api.delete("Account", "001B000001Lp1FxIAJ")
```

### `query`

```python
def query(self, soql: str) ‑> heroku_applink.data_api.record.RecordQueryResult
```
Query for records using the given SOQL string.

For example:

```python
result = await context.org.data_api.query("SELECT Id, Name FROM Account")

for record in result.records:
    # ...
```

If the returned `RecordQueryResult`'s `done` attribute is `False`, there are more
records to be returned. To retrieve these, use `DataAPI.query_more()`.

For more information, see the [Query REST API documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_query.htm).

### `query_more`

```python
def query_more(self, result: heroku_applink.data_api.record.RecordQueryResult) ‑> heroku_applink.data_api.record.RecordQueryResult
```
Query for more records, based on the given `RecordQueryResult`.

For example:

```python
result = await context.org.data_api.query("SELECT Id, Name FROM Account")

if not result.done:
    query_more_result = await context.org.data_api.query_more(result)
```

For more information, see the [Query More Results REST API documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_query_more_results.htm).

### `update`

```python
def update(self, record: heroku_applink.data_api.record.Record) ‑> str
```
Update an existing record based on the given `Record` object.

The given `Record` must contain an `Id` field. Returns the ID of the record that was updated.

For example:

```python
await context.org.data_api.update(
    Record(
        type="Account",
        fields={
            "Id": "001B000001Lp1FxIAJ",
            "Name": "New Name",
        },
    )
)
```