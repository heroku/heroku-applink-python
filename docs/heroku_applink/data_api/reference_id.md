Module heroku_applink.data_api.reference_id
===========================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

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