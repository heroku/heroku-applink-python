# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import base64
from typing import Any

import pytest

from heroku_applink import InvalidInboundDataError, parse_invocation_context

from .vectors import load_vectors

VECTORS = load_vectors("invocation-context.json")


@pytest.mark.parametrize("vector", VECTORS, ids=[v["name"] for v in VECTORS])
def test_vectors(vector: dict[str, Any]) -> None:
    def get_header(name: str) -> str | None:
        header: str | None = vector["header"] if name == "x-client-context" else None
        return header

    expected = vector.get("expected")
    if expected is None:
        with pytest.raises(InvalidInboundDataError):
            parse_invocation_context(get_header)
        return

    try:
        context = parse_invocation_context(get_header)
    except InvalidInboundDataError:
        if "error" not in vector:
            raise
        return
    assert context.request_id == expected["requestId"]
    assert context.namespace == expected["namespace"]
    assert context.org.id == expected["org"]["id"]
    assert context.org.domain_url == expected["org"]["domainUrl"]
    assert context.org.api_version == expected["org"]["apiVersion"]
    assert context.org.type is None
    assert context.user.id == expected["user"]["id"]
    assert context.user.username == expected["user"]["username"]
    if expected["credentials"] is None:
        assert context.credentials is None
    else:
        assert context.credentials is not None
        assert (
            context.credentials.access_token == expected["credentials"]["accessToken"]
        )
        assert context.credentials.expiration is None


def test_asks_for_the_header_in_lower_case() -> None:
    names: list[str] = []

    def get_header(name: str) -> None:
        names.append(name)

    with pytest.raises(InvalidInboundDataError):
        parse_invocation_context(get_header)
    assert names == ["x-client-context"]


def test_errors_dont_leak_the_header() -> None:
    header = base64.b64encode(b'{"accessToken":"secret-token","version":"1.0"').decode()
    with pytest.raises(InvalidInboundDataError) as info:
        parse_invocation_context(lambda _name: header)
    assert "secret-token" not in str(info.value)
    assert info.value.__cause__ is None
    assert info.value.__context__ is None
