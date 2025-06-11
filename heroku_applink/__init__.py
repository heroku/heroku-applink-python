"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from .authorization import Authorization
from .config import Config
from .context import ClientContext, get_client_context, set_client_context
from .data_api.record import QueriedRecord, Record, RecordQueryResult
from .data_api.reference_id import ReferenceId
from .data_api.unit_of_work import UnitOfWork
from .middleware import IntegrationWsgiMiddleware, IntegrationAsgiMiddleware
from .exceptions import ClientError, UnexpectedRestApiResponsePayload
from .connection import Connection

def get_authorization(developer_name: str, attachment_or_url: str|None=None) -> Authorization:
    """
    Get an Authorization object for a given developer name and attachment or URL.
    This Authorization object can be used to make SOQL queries to Salesforce via
    DataAPI.

    ```python
    import heroku_applink as sdk

    authorization = await sdk.get_authorization(
        developer_name="my-developer-name",
        attachment_or_url="HEROKU_APPLINK_BLUE",
    )

    query = "SELECT Id, Name FROM Account"
    result = await authorization.data_api.query(query)
    for record in result.records:
        print(f"Account: {record.get('Name')}")
    ```
    """
    return Authorization.find(developer_name, attachment_or_url)

__all__ = [
    "get_client_context",
    "set_client_context",
    "get_authorization",
    "Authorization",
    "Config",
    "Connection",
    "ClientContext",
    "QueriedRecord",
    "Record",
    "RecordQueryResult",
    "ReferenceId",
    "UnitOfWork",
    "IntegrationWsgiMiddleware",
    "IntegrationAsgiMiddleware",
    "ClientError",
    "UnexpectedRestApiResponsePayload",
]

