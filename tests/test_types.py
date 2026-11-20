# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import copy
import pickle
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from heroku_applink import (
    AppLinkContext,
    AuthorizationStatus,
    Credentials,
    HTTPError,
    InvocationAppLinkContext,
    Org,
    UnusableAuthorizationError,
    User,
    __version__,
)
from heroku_applink._version import USER_AGENT

CREDENTIALS = Credentials(
    access_token="secret-token",
    expiration=datetime(2026, 10, 13, 9, 15, 42, tzinfo=UTC),
)


def test_credentials_repr_redacts_the_access_token() -> None:
    assert repr(CREDENTIALS) == (
        "Credentials(access_token='[REDACTED]', "
        "expiration=datetime.datetime(2026, 10, 13, 9, 15, 42, tzinfo=datetime.timezone.utc))"
    )
    assert str(CREDENTIALS) == repr(CREDENTIALS)


def test_context_repr_redacts_the_access_token() -> None:
    context = InvocationAppLinkContext(
        org=Org(id="org", domain_url="https://example.tld", api_version="62.0"),
        user=User(id="user", username="user@example.tld"),
        request_id="request",
        credentials=CREDENTIALS,
    )
    assert "secret-token" not in repr(context)
    assert "secret-token" not in str(context)
    assert "[REDACTED]" in repr(context)
    assert isinstance(context, AppLinkContext)


def test_types_are_immutable() -> None:
    with pytest.raises(AttributeError):
        CREDENTIALS.access_token = "other"  # type: ignore[misc]


def test_user_agent_matches_package_version() -> None:
    pyproject = tomllib.loads(
        (Path(__file__).parent.parent / "pyproject.toml").read_text()
    )
    assert pyproject["project"]["version"] == __version__
    assert USER_AGENT == f"heroku-applink-python/{__version__}"


@pytest.mark.parametrize(
    "error",
    [
        HTTPError("not found", 404, "body"),
        UnusableAuthorizationError("failed", AuthorizationStatus.FAILED),
    ],
)
def test_errors_survive_pickling_and_copying(error: Exception) -> None:
    error.add_note("a note")
    for clone in (pickle.loads(pickle.dumps(error)), copy.copy(error)):
        assert type(clone) is type(error)
        assert str(clone) == str(error)
        assert vars(clone) == vars(error)
