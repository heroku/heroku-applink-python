Module heroku_applink.data_api.record
=====================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

Classes
-------

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