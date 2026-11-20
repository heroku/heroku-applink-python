# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OrgType(StrEnum):
    """The type of a Salesforce org, as returned by the AppLink API."""

    SALESFORCE_ORG = "SalesforceOrg"
    """A Salesforce org."""

    DATA_CLOUD_ORG = "DataCloudOrg"
    """A Data 360 org."""


class AuthorizationStatus(StrEnum):
    """The status of an authorization, as returned by the AppLink API.

    Only ``AUTHORIZED`` authorizations can be used. Apps only see the other
    statuses in an :class:`UnusableAuthorizationError`.

    See https://devcenter.heroku.com/articles/heroku-applink-api
    """

    AUTHORIZING = "authorizing"
    """The add-on is authorizing the user."""

    AUTHORIZED = "authorized"
    """The user is authorized and the authorization can be used."""

    DISCONNECTING = "disconnecting"
    """The add-on is removing the authorization."""

    DISCONNECTED = "disconnected"
    """The authorization has been removed."""

    FAILED = "failed"
    """Authorizing failed with an unexpected error."""


@dataclass(frozen=True, slots=True, kw_only=True)
class Org:
    """A Salesforce org that the app works with.

    Attributes:
        id: The ID of the org.
        domain_url: The org's My Domain URL. Pass it to a Salesforce client as
            the instance URL.
        api_version: The org's Salesforce API version, such as ``62.0``.
        type: The type of the org. Present in an
            :class:`AuthorizationAppLinkContext`, ``None`` in an
            :class:`InvocationAppLinkContext`.
    """

    id: str
    domain_url: str
    api_version: str
    type: OrgType | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    """A Salesforce user.

    Attributes:
        id: The ID of the user.
        username: The username of the user.
    """

    id: str
    username: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Credentials:
    """Credentials for calling Salesforce APIs.

    The ``repr`` redacts the access token, so it doesn't leak into logs by
    accident.

    Attributes:
        access_token: The Salesforce access token. Pass it to a Salesforce
            client as the bearer token.
        expiration: The instant the access token expires, in UTC. ``None`` if
            AppLink doesn't provide one.
    """

    access_token: str
    expiration: datetime | None = None

    def __repr__(self) -> str:
        return f"Credentials(access_token='[REDACTED]', expiration={self.expiration!r})"


@dataclass(frozen=True, slots=True, kw_only=True)
class AppLinkContext:
    """What every context has: the org and the user.

    Code that only needs the org and the user accepts an ``AppLinkContext``,
    so it works with both kinds of context.

    Attributes:
        org: The org the context belongs to.
        user: The user acting in the org.
    """

    org: Org
    user: User


@dataclass(frozen=True, slots=True, kw_only=True)
class InvocationAppLinkContext(AppLinkContext):
    """The context of an invocation from Salesforce.

    Decoded from the ``x-client-context`` header by
    :func:`parse_invocation_context`. There is one per inbound request. It
    describes the invoking user.

    Attributes:
        request_id: The ID of the invocation.
        namespace: The invoking org's namespace prefix. ``None`` when the org
            has none.
        credentials: Credentials for acting as the invoking user. ``None``
            when the invocation carries no access token.
    """

    request_id: str
    namespace: str | None = None
    credentials: Credentials | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizationMetadata:
    """Metadata of an authorization, as returned by the AppLink API.

    See https://devcenter.heroku.com/articles/heroku-applink-api

    Attributes:
        id: The ID of the authorization.
        developer_name: The developer name of the authorization.
        created_at: The instant the authorization was created, in UTC.
        created_by: Who created the authorization.
        created_via_app: The app the authorization was created through, if any.
        last_modified_at: The instant the authorization was last modified, in
            UTC.
        last_modified_by: Who last modified the authorization, if known.
        redirect_uri: The redirect URI of the authorization, if any.
    """

    id: str
    developer_name: str
    created_at: datetime
    created_by: str
    created_via_app: str | None = None
    last_modified_at: datetime
    last_modified_by: str | None = None
    redirect_uri: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizationAppLinkContext(AppLinkContext):
    """The context of a stored authorization.

    Returned by :func:`get_authorization`. It describes the user the
    authorization was made for. It is long-lived, and apps can cache and reuse
    it until ``credentials.expiration``.

    Attributes:
        authorization_metadata: The metadata of the authorization.
        credentials: Credentials for acting as the authorized user.
    """

    authorization_metadata: AuthorizationMetadata
    credentials: Credentials
