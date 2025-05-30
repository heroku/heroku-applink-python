Module heroku_applink.data_api.exceptions
=========================================
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

Classes
-------

<!-- python-clienterror.md -->
# `ClientError`

```python
class ClientError(*args, **kwargs)
```
Raised when the API request failed due to a connection error, timeout, or malformed HTTP response.

<!-- python-dataapierror.md -->
# `DataApiError`

```python
class DataApiError(*args, **kwargs)
```
Base class for Data API exceptions.

<!-- python-innersalesforcerestapierror.md -->
# `InnerSalesforceRestApiError`

```python
class InnerSalesforceRestApiError(*, message: str, error_code: str, fields: list[str])
```
An error returned from the Salesforce REST API.

## Instance variables

* `error_code: str`
    The error code for this error.

* `fields: list[str]`
    The field names where the error occurred.
    
    This will be empty for errors that aren't related to a specific field.

* `message: str`
    The description of this error.

<!-- python-missingfielderror.md -->
# `MissingFieldError`

```python
class MissingFieldError(*args, **kwargs)
```
Raised when the given `Record` must contain a field, but no such field was found.

<!-- python-salesforcerestapierror.md -->
# `SalesforceRestApiError`

```python
class SalesforceRestApiError(*, api_errors: list['InnerSalesforceRestApiError'])
```
Raised when the Salesforce REST API signalled error(s).

## Instance variables

* `api_errors: list[heroku_applink.data_api.exceptions.InnerSalesforceRestApiError]`
    A list of one or more errors returned from Salesforce REST API.

<!-- python-unexpectedrestapiresponsepayload.md -->
# `UnexpectedRestApiResponsePayload`

```python
class UnexpectedRestApiResponsePayload(*args, **kwargs)
```
Raised when the Salesforce REST API returned an unexpected payload.