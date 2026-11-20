# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

from typing import Any

import pytest

from heroku_applink import (
    ConfigurationError,
    OrgType,
    UnexpectedResponseError,
    UnusableAuthorizationError,
)
from heroku_applink._authorization import (
    authorization_path,
    parse_authorization_response,
    resolve_attachment,
)

from .vectors import load_vectors, parse_instant

RESPONSES = load_vectors("authorization-response.json")
ATTACHMENTS = load_vectors("attachment-resolution.json")
PATHS = load_vectors("request-path.json")


@pytest.mark.parametrize("vector", RESPONSES, ids=[v["name"] for v in RESPONSES])
def test_response_vectors(vector: dict[str, Any]) -> None:
    body = vector["body"].encode()
    if vector.get("error") == "unusable_authorization":
        with pytest.raises(UnusableAuthorizationError) as info:
            parse_authorization_response(body)
        assert info.value.status == vector["status"]
        return
    expected = vector.get("expected")
    if expected is None:
        with pytest.raises(UnexpectedResponseError) as unexpected:
            parse_authorization_response(body)
        assert unexpected.value.__context__ is None
        return

    try:
        context = parse_authorization_response(body)
    except UnexpectedResponseError as unexpected:
        if "error" not in vector:
            raise
        assert unexpected.__context__ is None
        return
    metadata = context.authorization_metadata
    expected_metadata = expected["authorizationMetadata"]
    assert metadata.id == expected_metadata["id"]
    assert metadata.developer_name == expected_metadata["developerName"]
    assert metadata.created_at == parse_instant(expected_metadata["createdAt"])
    assert metadata.created_at.utcoffset() is not None
    assert metadata.created_at.utcoffset().total_seconds() == 0  # type: ignore[union-attr]
    assert metadata.created_by == expected_metadata["createdBy"]
    assert metadata.created_via_app == expected_metadata["createdViaApp"]
    assert metadata.last_modified_at == parse_instant(
        expected_metadata["lastModifiedAt"]
    )
    assert metadata.last_modified_by == expected_metadata["lastModifiedBy"]
    assert metadata.redirect_uri == expected_metadata["redirectUri"]
    assert context.org.id == expected["org"]["id"]
    assert context.org.domain_url == expected["org"]["domainUrl"]
    assert context.org.api_version == expected["org"]["apiVersion"]
    assert context.org.type == OrgType(expected["org"]["type"])
    assert context.user.id == expected["user"]["id"]
    assert context.user.username == expected["user"]["username"]
    assert context.credentials.access_token == expected["credentials"]["accessToken"]
    assert context.credentials.expiration == parse_instant(
        expected["credentials"]["expiration"]
    )


def test_response_errors_dont_leak_the_body() -> None:
    body = (
        b'{"status":"authorized","org":{"user_auth":{"access_token":"secret-token"}}}'
    )
    with pytest.raises(UnexpectedResponseError) as info:
        parse_authorization_response(body)
    assert "secret-token" not in str(info.value)


@pytest.mark.parametrize("vector", ATTACHMENTS, ids=[v["name"] for v in ATTACHMENTS])
def test_attachment_vectors(vector: dict[str, Any]) -> None:
    expected = vector.get("expected")
    if expected is None:
        with pytest.raises(ConfigurationError):
            resolve_attachment(vector["env"], vector["attachment"])
        return
    resolved = resolve_attachment(vector["env"], vector["attachment"])
    assert resolved.api_url == expected["apiUrl"]
    assert resolved.token == expected["token"]
    assert resolved.app_id == expected["appId"]


@pytest.mark.parametrize("vector", PATHS, ids=[v["developerName"] for v in PATHS])
def test_path_vectors(vector: dict[str, Any]) -> None:
    assert authorization_path(vector["developerName"]) == vector["path"]
