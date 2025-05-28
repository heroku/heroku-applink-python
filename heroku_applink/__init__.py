"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from .authorization import Authorization
from .config import Config
from .context import ClientContext, Org, User
from .data_api.record import QueriedRecord, Record, RecordQueryResult
from .data_api.reference_id import ReferenceId
from .data_api.unit_of_work import UnitOfWork
from .middleware import IntegrationWsgiMiddleware, IntegrationAsgiMiddleware
from .exceptions import ClientError, UnexpectedRestApiResponsePayload
from .connection import Connection
from .middleware import client_context

def get_client_context() -> ClientContext:
    """
    Call `get_client_context` to get the client context for the current incoming
    request from Salesforce. This will be set by the `IntegrationWsgiMiddleware` or
    `IntegrationAsgiMiddleware` in your application and can only be used in requests
    that are routed through one of these middlewares.

    ```python
    import heroku_applink as sdk
    from fastapi import FastAPI

    app = FastAPI()
    app.add_middleware(sdk.IntegrationAsgiMiddleware, config=sdk.Config(request_timeout=5))

    @app.get("/accounts")
    async def get_accounts():
        context = sdk.get_client_context()

        query = "SELECT Id, Name FROM Account"
        result = await context.data_api.query(query)

        return {"accounts": [record.get("Name") for record in result.records]}
    ```
    """
    try:
      return client_context.get()
    except LookupError:
        # TODO: Add a more specific error message.
        raise ValueError("No client context found")

def get_authorization(config: Config) -> ClientContext:
    """
    Call `get_authorization` to get the client context for a given Heroku AppLink
    addon. This is useful when you want to query Salesforce data through a specific
    Heroku AppLink addon as opposed to getting information from the `x-client-context`
    header in a request from Salesforce.

    ```python
    import heroku_applink as sdk

    config = sdk.Config(
        developer_name="my-developer-name",
        attachment_or_url="HEROKU_APPLINK_BLUE",
    )
    context = await sdk.get_authorization(config)

    query = "SELECT Id, Name FROM Account"
    result = await context.data_api.query(query)
    for record in result.records:
        print(f"Account: {record.get('Name')}")
    ```
    """
    return Authorization(config).get_client_context()

__all__ = [
    "get_client_context",
    "get_authorization",
    "Authorization",
    "Config",
    "Connection",
    "client_context",
    "ClientContext",
    "Org",
    "QueriedRecord",
    "Record",
    "RecordQueryResult",
    "ReferenceId",
    "UnitOfWork",
    "User",
    "IntegrationWsgiMiddleware",
    "IntegrationAsgiMiddleware",
    "ClientError",
    "UnexpectedRestApiResponsePayload",
]

