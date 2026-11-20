# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import base64
from collections.abc import Callable

from ._errors import InvalidInboundDataError
from ._json import (
    InvalidFieldError,
    JsonObject,
    is_non_empty_string,
    optional_string,
    parse_json_object,
    required_object,
    required_string,
)
from ._types import Credentials, InvocationAppLinkContext, Org, User

_HEADER_NAME = "x-client-context"


def parse_invocation_context(
    get_header: Callable[[str], str | None],
) -> InvocationAppLinkContext:
    """Parses the context of an invocation from Salesforce.

    Reads the ``x-client-context`` header of an inbound request. The SDK trusts
    the header, because AppLink's Service Mesh authenticates requests before
    they reach the app.

    Example::

        context = parse_invocation_context(request.headers.get)

    See https://devcenter.heroku.com/articles/invoking-heroku-applink-apps

    Args:
        get_header: Returns the value of the inbound request's header with the
            given name, or ``None`` if the request doesn't have it. The SDK
            always passes header names in lower case.

    Returns:
        The context of the invocation.

    Raises:
        InvalidInboundDataError: If the header is missing or malformed.
    """
    value = get_header(_HEADER_NAME)
    if not isinstance(value, str) or value == "":
        raise InvalidInboundDataError(f"The {_HEADER_NAME} header is missing.")

    try:
        decoded = base64.b64decode(value, validate=True)
    except ValueError:
        decoded = None
    if decoded is None:
        raise InvalidInboundDataError(f"The {_HEADER_NAME} header is not valid base64.")

    data = parse_json_object(decoded)
    if data is None:
        raise InvalidInboundDataError(
            f"The {_HEADER_NAME} header doesn't contain a UTF-8 JSON object."
        )
    if data.get("version") != "1.0":
        raise InvalidInboundDataError(
            f"The {_HEADER_NAME} header doesn't have the supported version 1.0."
        )

    try:
        return _parse_context(data)
    except InvalidFieldError as error:
        field = error.field
    # Raised outside the except block so the error has no __context__.
    raise InvalidInboundDataError(
        f'The {_HEADER_NAME} header has no valid "{field}" field.'
    )


def _parse_context(data: JsonObject) -> InvocationAppLinkContext:
    user_context = required_object(data, "userContext")
    access_token = data.get("accessToken")
    if access_token is not None and not is_non_empty_string(access_token):
        raise InvalidFieldError("accessToken")

    return InvocationAppLinkContext(
        request_id=required_string(data, "requestId"),
        namespace=optional_string(data, "namespace"),
        org=Org(
            id=required_string(data, "orgId"),
            domain_url=required_string(data, "orgDomainUrl"),
            api_version=required_string(data, "apiVersion"),
        ),
        user=User(
            id=required_string(user_context, "userId", "userContext."),
            username=required_string(user_context, "username", "userContext."),
        ),
        credentials=None
        if access_token is None
        else Credentials(access_token=access_token),
    )
