"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import json
import base64

from contextvars import ContextVar
from dataclasses import dataclass

from .data_api import DataAPI
from .connection import Connection

__all__ = ["User", "Org", "ClientContext"]

@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    """
    Information about the Salesforce user that made the request.
    """

    id: str
    """
    The user's ID.

    For example: `005JS000000H123`
    """
    username: str
    """
    The username of the user.

    For example: `user@example.tld`
    """


@dataclass(frozen=True, kw_only=True, slots=True)
class Org:
    """Information about the Salesforce org and the user that made the request."""

    id: str
    """
    The Salesforce org ID.

    For example: `00DJS0000000123ABC`
    """

    domain_url: str
    """
    The canonical URL of the Salesforce org.

    This URL never changes. Use this URL when making API calls to your org.

    For example: `https://example-domain-url.my.salesforce.com`
    """
    user: User
    """The currently logged in user."""


@dataclass(frozen=True, kw_only=True, slots=True)
class ClientContext:
    """Information about the Salesforce org that made the request."""

    org: Org
    """Information about the Salesforce org and the user that made the request."""
    data_api: DataAPI
    """An initialized data API client instance for interacting with data in the org."""
    request_id: str
    """Request ID from the Salesforce org."""
    access_token: str
    """Valid access token for the current context org/user."""
    api_version: str
    """API version of the Salesforce component that made the request."""
    namespace: str | None = None
    """Namespace of the Salesforce component that made the request."""

    @classmethod
    def from_header(cls, header: str, connection: Connection):
        decoded = base64.b64decode(header)
        data = json.loads(decoded)

        return cls(
            org=Org(
                id=data["orgId"],
                domain_url=data["orgDomainUrl"],
                user=User(
                    id=data["userContext"]["userId"],
                    username=data["userContext"]["username"],
                ),
            ),
            request_id=data["requestId"],
            access_token=data["accessToken"],
            api_version=data["apiVersion"],
            namespace=data.get("namespace"),  # Use get() to handle None case
            data_api=DataAPI(
                org_domain_url=data["orgDomainUrl"],
                api_version=data["apiVersion"],
                access_token=data["accessToken"],
                connection=connection,
            ),
        )

# ContextVars for request-scoped data
client_context: ContextVar[ClientContext] = ContextVar("client_context")

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
        raise ValueError("No client context found")

def set_client_context(new_client_context: ClientContext):
    """
    Set the client context for the current request.
    """
    client_context.set(new_client_context)
