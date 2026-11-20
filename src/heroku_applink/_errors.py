# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

from typing import Any

from ._types import AuthorizationStatus


class AppLinkError(Exception):
    """The common base class of all errors the SDK raises."""


class InvalidInboundDataError(AppLinkError):
    """Data sent to the app is missing or can't be parsed.

    For example, a missing or malformed ``x-client-context`` header.
    """


class ConfigurationError(AppLinkError):
    """An authorization lookup can't start.

    Its input or the app's config vars are missing or invalid. Raised before
    any request is sent.
    """


class TransportError(AppLinkError):
    """A request to the AppLink API didn't complete.

    For example, because the connection failed or timed out.
    """


class HTTPError(AppLinkError):
    """The AppLink API responded with a status other than 2xx.

    Attributes:
        status: The HTTP status of the response, such as ``404`` for an unknown
            authorization.
        body: The response body as UTF-8 text, with invalid bytes replaced. At
            most 1 MiB is read.
    """

    def __init__(self, message: str, status: int, body: str) -> None:
        super().__init__(message)
        self.status = status
        self.body = body

    def __reduce__(self) -> tuple[Any, ...]:
        return type(self), (self.args[0], self.status, self.body), self.__dict__


class UnusableAuthorizationError(AppLinkError):
    """The AppLink API returned the authorization, but it isn't authorized.

    For example, because it is still being authorized or was disconnected.

    Attributes:
        status: The status of the authorization.
    """

    def __init__(self, message: str, status: AuthorizationStatus) -> None:
        super().__init__(message)
        self.status = status

    def __reduce__(self) -> tuple[Any, ...]:
        return type(self), (self.args[0], self.status), self.__dict__


class UnexpectedResponseError(AppLinkError):
    """The AppLink API responded with a 2xx status, but unexpected content.

    For example, a response with a missing required field.
    """
