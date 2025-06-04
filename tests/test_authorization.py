import pytest

import aiohttp
from aioresponses import aioresponses
from typing import Dict, Any

from heroku_applink.connection import Connection
from heroku_applink.data_api import DataAPI
from heroku_applink.authorization import (
    Authorization,
    _resolve_addon_config_by_attachment_or_color,
    _resolve_addon_config_by_url,
    _resolve_attachment_or_url,
    _is_valid_url,
)
from heroku_applink.authorization import Org as AuthorizationOrg

# A sample valid response payload from the add-on
VALID_RESPONSE: Dict[str, Any] = {
    "id": "b8bc7bcb-89c3-45c0-b7b7-4fb4427e598a",
    "status": "authorized",
    "org": {
        "id": "00DSG00000DGEIr2AP",
        "developer_name": "productionOrg2",
        "instance_url": "https://dmomain.my.salesforce.com",
        "type": "SalesforceOrg",
        "api_version": "57.0",
        "user_auth": {
            "username": "admin@whatever.org",
            "user_id": "005...",
            "access_token": "00DSG00000DGEIr2AP!<token>"
        }
    },
    "created_at": "2025-03-06T18:20:42.226577Z",
    "created_by": "foo@heroku.com",
    "created_via_app": "test-app",
    "last_modified_at": "2025-03-09T18:20:42.226577Z",
    "last_modified_by": "foo@heroku.com",
    "redirect_uri": "https://test-app.herokuapp.com",
}

VALID_RESPONSE_NO_REDIRECT_URI: Dict[str, Any] = {
      "id": "b8bc7bcb-89c3-45c0-b7b7-4fb4427e598a",
    "status": "authorized",
    "org": {
        "id": "00DSG00000DGEIr2AP",
        "developer_name": "productionOrg2",
        "instance_url": "https://dmomain.my.salesforce.com",
        "type": "SalesforceOrg",
        "api_version": "57.0",
        "user_auth": {
            "username": "admin@whatever.org",
            "user_id": "005...",
            "access_token": "00DSG00000DGEIr2AP!<token>"
        }
    },
    "created_at": "2025-03-06T18:20:42.226577Z",
    "created_by": "foo@heroku.com",
    "created_via_app": "test-app",
    "last_modified_at": "2025-03-09T18:20:42.226577Z",
    "last_modified_by": "foo@heroku.com",
}

def assert_authorization_is_valid(authorization: Authorization):
    assert isinstance(authorization, Authorization)
    assert isinstance(authorization.connection, Connection)
    assert isinstance(authorization.data_api, DataAPI)
    assert isinstance(authorization.org, AuthorizationOrg)

    assert authorization.id is not None
    assert authorization.status is not None
    assert authorization.org is not None

    assert authorization.org.id is not None
    assert authorization.org.developer_name is not None
    assert authorization.org.instance_url is not None
    assert authorization.org.type is not None
    assert authorization.org.api_version is not None
    assert authorization.org.user_auth is not None

    assert authorization.org.user_auth.username is not None
    assert authorization.org.user_auth.user_id is not None
    assert authorization.org.user_auth.access_token is not None

@pytest.mark.asyncio
async def test_attachment_based_success(monkeypatch):
    developer_name = "devName"

    # Call without trailing slash base, ensure rstrip
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=200,
            payload=VALID_RESPONSE
        )

        authorization = await Authorization.find(developer_name)

        assert_authorization_is_valid(authorization)

@pytest.mark.asyncio
async def test_attachment_based_success_no_redirect_uri(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=200,
            payload=VALID_RESPONSE_NO_REDIRECT_URI
        )

        authorization = await Authorization.find(developer_name)

        assert_authorization_is_valid(authorization)
        assert authorization.redirect_uri is None

@pytest.mark.asyncio
async def test_attachment_with_server_side_error(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=500,
            payload={"error": "Internal Server Error"}
        )

        with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as exc_info:
            await Authorization.find(developer_name)

        assert exc_info.value.status, 500

@pytest.mark.asyncio
async def test_attachment_with_client_side_error(monkeypatch):
    developer_name = "devName"

    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    with aioresponses() as m:
        m.get(
            f"https://api.test/authorizations/{developer_name}",
            status=400,
            payload={"error": "Bad Request"}
        )

        with pytest.raises(aiohttp.client_exceptions.ClientResponseError) as exc_info:
            await Authorization.find(developer_name)

        assert exc_info.value.status, 400

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
