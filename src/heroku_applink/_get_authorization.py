# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import os
from collections.abc import Mapping
from urllib.parse import SplitResult, urlsplit

from ._authorization import (
    authorization_path,
    parse_authorization_response,
    resolve_attachment,
)
from ._errors import ConfigurationError, HTTPError, UnexpectedResponseError
from ._http import HttpSettings, get_with_retries
from ._types import AuthorizationAppLinkContext
from ._version import USER_AGENT


def get_authorization(
    developer_name: str, attachment: str | None = None
) -> AuthorizationAppLinkContext:
    """Looks up a stored authorization through the AppLink API.

    Every call sends a request to the AppLink API. Apps can keep the returned
    context and reuse it until ``credentials.expiration``.

    This function blocks while it requests and retries. Async apps can run it
    with :func:`asyncio.to_thread` to keep the event loop responsive.

    Example::

        context = get_authorization("<my-authorization>")
        salesforce = Salesforce(
            instance_url=context.org.domain_url,
            session_id=context.credentials.access_token,
            version=context.org.api_version,
        )

    With another attachment::

        # By name, reads HEROKU_APPLINK_PURPLE_API_URL and HEROKU_APPLINK_PURPLE_TOKEN
        context = get_authorization("<my-authorization>", attachment="HEROKU_APPLINK_PURPLE")

        # By color, reads the same config vars as the name
        context = get_authorization("<my-authorization>", attachment="purple")

        # By API URL, uses the attachment whose _API_URL config var holds that URL
        api_url = os.environ["HEROKU_APPLINK_PURPLE_API_URL"]
        context = get_authorization("<my-authorization>", attachment=api_url)

    See https://devcenter.heroku.com/articles/heroku-applink-api

    Args:
        developer_name: The developer name of the authorization.
        attachment: The AppLink add-on attachment to use, by name (such as
            ``HEROKU_APPLINK_PURPLE``), color (such as ``purple``), or API URL.
            Without it, the SDK uses the default attachment ``HEROKU_APPLINK``.

    Returns:
        The context of the authorization.

    Raises:
        ConfigurationError: If the developer name or attachment is empty, the
            developer name contains lone surrogates, or the config vars are
            missing or invalid.
        TransportError: If the request to the AppLink API didn't complete.
        HTTPError: If the AppLink API responded with a status other than 2xx.
        UnusableAuthorizationError: If the authorization isn't authorized.
        UnexpectedResponseError: If the response doesn't have the expected
            content.
    """
    return get_authorization_with(
        os.environ, HttpSettings(), developer_name, attachment
    )


def get_authorization_with(
    env: Mapping[str, str],
    settings: HttpSettings,
    developer_name: str,
    attachment: str | None = None,
) -> AuthorizationAppLinkContext:
    if developer_name == "":
        raise ConfigurationError("The developer name must not be empty.")
    try:
        developer_name.encode("utf-8")
    except UnicodeEncodeError:
        raise ConfigurationError(
            "The developer name must not contain lone surrogates."
        ) from None
    resolved = resolve_attachment(env, attachment)
    url = _split_url(resolved.api_url)

    response = get_with_retries(
        url,
        url.path + authorization_path(developer_name),
        {
            "Authorization": f"Bearer {resolved.token}",
            "X-App-UUID": resolved.app_id,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        settings,
    )

    if not 200 <= response.status <= 299:
        raise HTTPError(
            f"The AppLink API responded with HTTP status {response.status}.",
            response.status,
            response.body.decode("utf-8", errors="replace"),
        )
    if response.body_too_large:
        raise UnexpectedResponseError("The AppLink API response is larger than 1 MiB.")
    return parse_authorization_response(response.body)


def _split_url(api_url: str) -> SplitResult:
    url = None
    try:
        url = urlsplit(api_url)
        _ = url.port
    except ValueError:
        url = None
    if url is None or not url.hostname:
        raise ConfigurationError("The AppLink API URL is not a valid URL.")
    return url
