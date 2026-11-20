# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import ssl
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler

import pytest

from heroku_applink import (
    ConfigurationError,
    HTTPError,
    TransportError,
    UnexpectedResponseError,
    UnusableAuthorizationError,
)
from heroku_applink._get_authorization import get_authorization_with
from heroku_applink._http import HttpSettings
from heroku_applink._version import USER_AGENT

from .tls_server import TlsServer, respond_with, tls_server
from .vectors import load_vectors

MIB = 1024 * 1024
VALID_BODY: str = load_vectors("authorization-response.json")[0]["body"]


@pytest.fixture(scope="module")
def server() -> Iterator[TlsServer]:
    with tls_server() as server:
        yield server


@pytest.fixture
def settings(server: TlsServer) -> HttpSettings:
    return HttpSettings(
        timeout=0.5,
        retry_delays=(0.001, 0.002, 0.003),
        ssl_context=server.client_context(),
    )


@pytest.fixture
def env(server: TlsServer) -> dict[str, str]:
    return {
        "HEROKU_APPLINK_API_URL": f"{server.url}/addons/abc/",
        "HEROKU_APPLINK_TOKEN": "addon-token",
        "HEROKU_APP_ID": "app-uuid",
    }


def test_sends_the_documented_request(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(200, VALID_BODY))
    context = get_authorization_with(env, settings, "my org/x")
    assert context.credentials.access_token == "00DJS0000000123!AQ0AQ.token"
    [request] = server.requests
    assert request.command == "GET"
    assert request.path == "/addons/abc/authorizations/my%20org%2Fx"
    assert request.headers["Authorization"] == "Bearer addon-token"
    assert request.headers["X-App-UUID"] == "app-uuid"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["User-Agent"] == USER_AGENT


def test_configuration_errors_send_no_request(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(200, VALID_BODY))
    with pytest.raises(ConfigurationError):
        get_authorization_with(env, settings, "")
    with pytest.raises(ConfigurationError):
        get_authorization_with(env, settings, "x", "")
    with pytest.raises(ConfigurationError):
        get_authorization_with({**env, "HEROKU_APP_ID": ""}, settings, "x")
    with pytest.raises(ConfigurationError):
        get_authorization_with(env, settings, "a\udcffb")
    assert server.requests == []


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("HEROKU_APPLINK_TOKEN", "secret\ntoken"),
        ("HEROKU_APPLINK_TOKEN", "secret-tok€n"),
        ("HEROKU_APP_ID", "app-uuid\r\nX-Injected: secret"),
        ("HEROKU_APPLINK_API_URL", "https://127.0.0.1:1/a b"),
        ("HEROKU_APPLINK_API_URL", "https:///addons/abc"),
    ],
)
def test_config_vars_the_request_cant_be_built_from(
    server: TlsServer,
    settings: HttpSettings,
    env: dict[str, str],
    name: str,
    value: str,
) -> None:
    server.respond(respond_with(200, VALID_BODY))
    with pytest.raises(ConfigurationError) as info:
        get_authorization_with({**env, name: value}, settings, "x")
    assert "secret" not in str(info.value)
    assert info.value.__cause__ is None
    assert info.value.__context__ is None or info.value.__suppress_context__
    assert server.requests == []


def test_reports_status_and_body(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(404, b'{"message":"not found"}'))
    with pytest.raises(HTTPError) as info:
        get_authorization_with(env, settings, "x")
    assert info.value.status == 404
    assert info.value.body == '{"message":"not found"}'
    assert len(server.requests) == 1


def test_replaces_invalid_utf8_in_error_bodies(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(400, b"a\xffb"))
    with pytest.raises(HTTPError) as info:
        get_authorization_with(env, settings, "x")
    assert info.value.body == "a�b"


def test_doesnt_follow_redirects(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(302, headers={"Location": "/elsewhere"}))
    with pytest.raises(HTTPError) as info:
        get_authorization_with(env, settings, "x")
    assert info.value.status == 302
    assert len(server.requests) == 1


@pytest.mark.parametrize("status", [429, 500, 503])
def test_retries(
    server: TlsServer, settings: HttpSettings, env: dict[str, str], status: int
) -> None:
    server.respond(respond_with(status, "busy"), respond_with(200, VALID_BODY))
    get_authorization_with(env, settings, "x")
    assert len(server.requests) == 2


def test_reports_the_last_error_after_three_retries(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(
        respond_with(500, "first"),
        respond_with(500, "second"),
        respond_with(500, "third"),
        respond_with(503, "last"),
    )
    with pytest.raises(HTTPError) as info:
        get_authorization_with(env, settings, "x")
    assert info.value.status == 503
    assert info.value.body == "last"
    assert len(server.requests) == 4


def test_doesnt_retry_other_responses(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(400, "bad"), respond_with(200, VALID_BODY))
    with pytest.raises(HTTPError):
        get_authorization_with(env, settings, "x")
    assert len(server.requests) == 1


def test_doesnt_retry_unusable_authorizations(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(
        respond_with(200, '{"status":"failed"}'), respond_with(200, VALID_BODY)
    )
    with pytest.raises(UnusableAuthorizationError):
        get_authorization_with(env, settings, "x")
    assert len(server.requests) == 1


def hang(_request: BaseHTTPRequestHandler) -> None:
    time.sleep(1)


def test_retries_after_timeouts(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(hang)
    with pytest.raises(TransportError):
        get_authorization_with(env, settings, "x")
    assert len(server.requests) == 4


def test_times_out_while_reading_a_slow_body(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    def slow_body(request: BaseHTTPRequestHandler) -> None:
        request.send_response(200)
        request.send_header("Content-Length", "100")
        request.end_headers()
        for _ in range(10):
            request.wfile.write(b" ")
            request.wfile.flush()
            time.sleep(0.1)

    server.respond(slow_body)
    no_retries = HttpSettings(
        timeout=0.5, retry_delays=(), ssl_context=settings.ssl_context
    )
    with pytest.raises(TransportError):
        get_authorization_with(env, no_retries, "x")


def test_connection_failures(settings: HttpSettings, env: dict[str, str]) -> None:
    with pytest.raises(TransportError) as info:
        get_authorization_with(
            {**env, "HEROKU_APPLINK_API_URL": "https://127.0.0.1:1"}, settings, "x"
        )
    assert isinstance(info.value.__cause__, ConnectionRefusedError)


def test_invalid_hosts(settings: HttpSettings, env: dict[str, str]) -> None:
    with pytest.raises(TransportError) as info:
        get_authorization_with(
            {**env, "HEROKU_APPLINK_API_URL": "https://a..example.com"}, settings, "x"
        )
    assert isinstance(info.value.__cause__, UnicodeError)


def test_retries_untrusted_certificates(server: TlsServer, env: dict[str, str]) -> None:
    server.respond(respond_with(200, VALID_BODY))
    started = time.monotonic()
    with pytest.raises(TransportError) as info:
        get_authorization_with(env, HttpSettings(timeout=0.5, retry_delays=(0.3,)), "x")
    assert time.monotonic() - started >= 0.3
    assert isinstance(info.value.__cause__, ssl.SSLCertVerificationError)


def test_rejects_2xx_bodies_larger_than_1_mib(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(200, VALID_BODY + " " * MIB))
    with pytest.raises(UnexpectedResponseError):
        get_authorization_with(env, settings, "x")


def test_accepts_2xx_bodies_of_exactly_1_mib(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(
        respond_with(200, VALID_BODY + " " * (MIB - len(VALID_BODY.encode())))
    )
    get_authorization_with(env, settings, "x")


def test_truncates_error_bodies_to_1_mib(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(respond_with(400, "x" * 2 * MIB))
    with pytest.raises(HTTPError) as info:
        get_authorization_with(env, settings, "x")
    assert len(info.value.body) == MIB


def test_unexpected_responses_dont_leak_the_body(
    server: TlsServer, settings: HttpSettings, env: dict[str, str]
) -> None:
    server.respond(
        respond_with(
            200,
            '{"status":"authorized","org":{"user_auth":{"access_token":"secret-token"}}}',
        )
    )
    with pytest.raises(UnexpectedResponseError) as info:
        get_authorization_with(env, settings, "x")
    assert "secret-token" not in str(info.value)
