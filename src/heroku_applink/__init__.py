# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

"""Heroku AppLink SDK for Python.

Use :func:`parse_invocation_context` to get the context of an invocation from
Salesforce, and :func:`get_authorization` to look up a stored authorization.

See https://devcenter.heroku.com/articles/heroku-applink
"""

from ._errors import (
    AppLinkError,
    ConfigurationError,
    HTTPError,
    InvalidInboundDataError,
    TransportError,
    UnexpectedResponseError,
    UnusableAuthorizationError,
)
from ._get_authorization import get_authorization
from ._invocation import parse_invocation_context
from ._types import (
    AppLinkContext,
    AuthorizationAppLinkContext,
    AuthorizationMetadata,
    AuthorizationStatus,
    Credentials,
    InvocationAppLinkContext,
    Org,
    OrgType,
    User,
)
from ._version import VERSION as __version__

__all__ = [
    "AppLinkContext",
    "AppLinkError",
    "AuthorizationAppLinkContext",
    "AuthorizationMetadata",
    "AuthorizationStatus",
    "ConfigurationError",
    "Credentials",
    "HTTPError",
    "InvalidInboundDataError",
    "InvocationAppLinkContext",
    "Org",
    "OrgType",
    "TransportError",
    "UnexpectedResponseError",
    "UnusableAuthorizationError",
    "User",
    "__version__",
    "get_authorization",
    "parse_invocation_context",
]
