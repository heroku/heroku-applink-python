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
    try:
      return client_context.get()
    except LookupError:
        # TODO: Add a more specific error message.
        raise ValueError("No client context found")

def get_authorization(config: Config) -> ClientContext:
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

