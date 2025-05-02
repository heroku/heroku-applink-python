Module heroku_applink.data_api.reference_id
===========================================

Classes
-------

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