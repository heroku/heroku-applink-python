import pytest

import aiohttp
from aioresponses import aioresponses
from typing import Dict, Any

from heroku_applink.config import Config
from heroku_applink.authorization import (
    Authorization,
    _resolve_addon_config_by_attachment_or_color,
    _resolve_addon_config_by_url,
    _resolve_attachment_or_url,
    _is_valid_url,
)
from heroku_applink.context import ClientContext

# A sample valid response payload from the add-on
VALID_RESPONSE: Dict[str, Any] = {
    "org_id": "00DTEST123",
    "org_domain_url": "https://example.my.salesforce.com/",
    "user_id": "005TEST456",
    "username": "user@example.com",
    "request_id": "REQ-789",
    "access_token": "TOKEN_ABC",
    "api_version": "v52.0",
    "namespace": "testns",
}

@pytest.mark.asyncio
async def test_attachment_based_success(monkeypatch):
    developer_name = "devName"

    # Call without trailing slash base, ensure rstrip
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    authorization = Authorization(Config(
        developer_name=developer_name,
        attachment_or_url=None
    ))

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=200,
            payload=VALID_RESPONSE
        )

        context = await authorization.get_client_context()

        assert isinstance(context, ClientContext)
        assert context is not None

        assert context.org is not None
        assert context.org.id is not None
        assert context.org.domain_url is not None
        assert context.org.user is not None
        assert context.org.user.id is not None
        assert context.request_id is not None

@pytest.mark.asyncio
async def test_attachment_with_server_side_error(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    authorization = Authorization(Config(
        developer_name=developer_name,
        attachment_or_url=None
    ))

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=500,
            payload={"error": "Internal Server Error"}
        )

        with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as exc_info:
            await authorization.get_client_context()

        assert exc_info.value.status, 500

@pytest.mark.asyncio
async def test_attachment_with_client_side_error(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    authorization = Authorization(Config(
        developer_name=developer_name,
        attachment_or_url=None
    ))

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=400,
            payload={"error": "Bad Request"}
        )

        with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as exc_info:
            await authorization.get_client_context()

        assert exc_info.value.status, 400

@pytest.mark.asyncio
async def test_attachment_with_timeout_error(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    authorization = Authorization(Config(
        developer_name=developer_name,
        attachment_or_url=None
    ))

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            exception=aiohttp.ServerTimeoutError
        )

        with pytest.raises(aiohttp.ServerTimeoutError) as exc_info:
            await authorization.get_client_context()

        assert isinstance(exc_info.value, aiohttp.ServerTimeoutError)

def test_resolve_attachment_or_url(monkeypatch):
    # Set URL env var and corresponding token
    monkeypatch.setenv('EXAMPLE_API_URL', 'https://api.test.com')
    monkeypatch.setenv('EXAMPLE_TOKEN', 'url-token')

    auth = _resolve_attachment_or_url("EXAMPLE")

    assert auth is not None
    assert auth.api_url == "https://api.test.com"
    assert auth.token == "url-token"

    auth = _resolve_attachment_or_url("https://api.test.com")

    assert auth is not None
    assert auth.api_url == "https://api.test.com"
    assert auth.token == "url-token"

def test_resolve_addon_config_by_url(monkeypatch):
    # Set URL env var and corresponding token
    monkeypatch.setenv('EXAMPLE_API_URL', 'https://api.test.com')
    monkeypatch.setenv('EXAMPLE_TOKEN', 'url-token')

    auth = _resolve_addon_config_by_url("https://api.test.com")

    assert auth is not None
    assert auth.api_url == "https://api.test.com"
    assert auth.token == "url-token"

def test_resolve_by_url_case_insensitive(monkeypatch):
    # URL matching should be case-insensitive
    monkeypatch.setenv('CASE_API_URL', 'https://Case.Example.COM')
    monkeypatch.setenv('CASE_TOKEN', 'case-token')

    auth = _resolve_addon_config_by_url('https://case.example.com')

    assert auth is not None
    assert auth.api_url == 'https://Case.Example.COM'
    assert auth.token == 'case-token'

def test_resolve_by_url_missing(monkeypatch):
    monkeypatch.delenv('MISSING_API_URL', raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        _resolve_addon_config_by_url('https://doesnotexist')

    assert 'Heroku Applink config not found for API URL' in str(exc_info.value)

def test_resolve_addon_config_by_attachment_or_color_direct(monkeypatch):
    # Set direct attachment env vars
    monkeypatch.setenv('MYADDON_API_URL', 'https://api.example.com')
    monkeypatch.setenv('MYADDON_TOKEN', 'secret-token')

    auth = _resolve_addon_config_by_attachment_or_color('myaddon')

    assert auth is not None
    assert auth.api_url == "https://api.example.com"
    assert auth.token == "secret-token"

def test_resolve_by_attachment_or_color_missing(monkeypatch):
    monkeypatch.delenv('HEROKU_APPLINK_BLUE_API_URL', raising=False)
    monkeypatch.delenv('HEROKU_APPLINK_BLUE_TOKEN', raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        _resolve_addon_config_by_attachment_or_color('HEROKU_APPLINK_BLUE')

    assert 'Heroku Applink config not found for \'HEROKU_APPLINK_BLUE\'' in str(exc_info.value)

def test_resolve_by_color_fallback(monkeypatch):
    # Remove direct and set fallback under HEROKU_APPLINK
    monkeypatch.delenv('COLOR_API_URL', raising=False)
    monkeypatch.delenv('COLOR_TOKEN', raising=False)
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_API_URL', 'https://color.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_TOKEN', 'color-token')

    auth = _resolve_addon_config_by_attachment_or_color("color")

    assert auth is not None
    assert auth.api_url == "https://color.example.com"
    assert auth.token == "color-token"

def test_is_valid_url():
    assert _is_valid_url("https://api.test.com") is True
    assert _is_valid_url("http://api.test.com") is True
    assert _is_valid_url("api.test.com") is False
    assert _is_valid_url("test") is False
    assert _is_valid_url("https://") is False
    assert _is_valid_url("https://api.test.com/") is True
