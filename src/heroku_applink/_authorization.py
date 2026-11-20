# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import re
import string
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

from ._errors import (
    ConfigurationError,
    UnexpectedResponseError,
    UnusableAuthorizationError,
)
from ._json import (
    InvalidFieldError,
    JsonObject,
    optional_string,
    parse_json_object,
    required_object,
    required_string,
)
from ._types import (
    AuthorizationAppLinkContext,
    AuthorizationMetadata,
    AuthorizationStatus,
    Credentials,
    Org,
    OrgType,
    User,
)

_ABSOLUTE_URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://")
_HTTPS_URL = re.compile(r"https://", re.IGNORECASE | re.ASCII)
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_MAX_EXPIRATION = (datetime.max.replace(tzinfo=UTC) - _EPOCH) // timedelta(
    milliseconds=1
)
_TO_ASCII_UPPER = str.maketrans(string.ascii_lowercase, string.ascii_uppercase)
_TO_ASCII_LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


@dataclass(frozen=True, slots=True)
class ResolvedAttachment:
    api_url: str
    token: str = field(repr=False)
    app_id: str


def resolve_attachment(
    env: Mapping[str, str], attachment: str | None
) -> ResolvedAttachment:
    if attachment is None:
        api_url_var = "HEROKU_APPLINK_API_URL"
        token_var = "HEROKU_APPLINK_TOKEN"
    elif attachment == "":
        raise ConfigurationError("The attachment must not be empty.")
    elif _ABSOLUTE_URL.match(attachment):
        wanted = _normalize_url(attachment)
        matches = sorted(
            name
            for name, value in env.items()
            if name.endswith("_API_URL") and _normalize_url(value) == wanted
        )
        if not matches:
            raise ConfigurationError(
                f"No config var ending in _API_URL matches the attachment URL {attachment}."
            )
        if len(matches) > 1:
            raise ConfigurationError(
                f"Several config vars match the attachment URL {attachment}: {', '.join(matches)}."
            )
        api_url_var = matches[0]
        token_var = api_url_var.removesuffix("API_URL") + "TOKEN"
    else:
        name = attachment.translate(_TO_ASCII_UPPER)
        if env.get(f"{name}_API_URL") and env.get(f"{name}_TOKEN"):
            api_url_var = f"{name}_API_URL"
            token_var = f"{name}_TOKEN"
        else:
            api_url_var = f"HEROKU_APPLINK_{name}_API_URL"
            token_var = f"HEROKU_APPLINK_{name}_TOKEN"

    api_url = _required_config_var(env, api_url_var)
    token = _required_config_var(env, token_var)
    app_id = _required_config_var(env, "HEROKU_APP_ID")
    if not _HTTPS_URL.match(api_url):
        raise ConfigurationError(
            f"The config var {api_url_var} must contain an https URL."
        )
    return ResolvedAttachment(
        api_url=api_url.removesuffix("/"), token=token, app_id=app_id
    )


def _required_config_var(env: Mapping[str, str], name: str) -> str:
    value = env.get(name)
    if not value:
        raise ConfigurationError(f"The config var {name} is missing or empty.")
    return value


def _normalize_url(url: str) -> str:
    return url.translate(_TO_ASCII_LOWER).removesuffix("/")


def authorization_path(developer_name: str) -> str:
    return "/authorizations/" + quote(developer_name, safe="", encoding="utf-8")


def parse_authorization_response(body: bytes) -> AuthorizationAppLinkContext:
    data = parse_json_object(body)
    if data is None:
        raise UnexpectedResponseError("The AppLink API response is not a JSON object.")
    try:
        return _parse_authorization(data)
    except InvalidFieldError as error:
        field = error.field
    # Raised outside the except block so the error has no __context__.
    raise UnexpectedResponseError(
        f'The AppLink API response has no valid "{field}" field.'
    )


def _parse_authorization(data: JsonObject) -> AuthorizationAppLinkContext:
    status = data.get("status")
    if not isinstance(status, str) or status not in AuthorizationStatus:
        raise InvalidFieldError("status")
    if status != AuthorizationStatus.AUTHORIZED:
        raise UnusableAuthorizationError(
            f"The authorization has the status {status} instead of authorized.",
            AuthorizationStatus(status),
        )

    org = required_object(data, "org")
    user_auth = required_object(org, "user_auth", "org.")
    org_type = org.get("type")
    if not isinstance(org_type, str) or org_type not in OrgType:
        raise InvalidFieldError("org.type")

    return AuthorizationAppLinkContext(
        authorization_metadata=AuthorizationMetadata(
            id=required_string(data, "id"),
            developer_name=required_string(org, "developer_name", "org."),
            created_at=_required_timestamp(data, "created_at"),
            created_by=required_string(data, "created_by"),
            created_via_app=optional_string(data, "created_via_app"),
            last_modified_at=_required_timestamp(data, "last_modified_at"),
            last_modified_by=optional_string(data, "last_modified_by"),
            redirect_uri=optional_string(data, "redirect_uri"),
        ),
        org=Org(
            id=required_string(org, "id", "org."),
            domain_url=required_string(org, "instance_url", "org."),
            api_version=required_string(org, "api_version", "org."),
            type=OrgType(org_type),
        ),
        user=User(
            id=required_string(user_auth, "user_id", "org.user_auth."),
            username=required_string(user_auth, "username", "org.user_auth."),
        ),
        credentials=Credentials(
            access_token=required_string(user_auth, "access_token", "org.user_auth."),
            expiration=_optional_expiration(user_auth),
        ),
    )


def _required_timestamp(data: JsonObject, field: str) -> datetime:
    value = required_string(data, field)
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        raise InvalidFieldError(field) from None
    if timestamp.tzinfo is None:
        raise InvalidFieldError(field)
    return timestamp.astimezone(UTC)


def _optional_expiration(user_auth: JsonObject) -> datetime | None:
    value = user_auth.get("expiration")
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= _MAX_EXPIRATION:
        raise InvalidFieldError("org.user_auth.expiration")
    return None if value == 0 else _EPOCH + timedelta(milliseconds=value)
