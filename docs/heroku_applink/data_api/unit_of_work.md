Module heroku_applink.data_api.unit_of_work
===========================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

Classes
-------

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