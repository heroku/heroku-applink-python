import pytest
from unittest.mock import AsyncMock, patch
from heroku_applink.addons.heroku_applink import (
    get_authorization,
    resolve_addon_config_by_attachment,
    resolve_addon_config_by_url,
    validate_url
)
import os

@pytest.mark.asyncio
async def test_get_authorization_success():
    """Test successful authorization request."""
    # Mock the environment variables
    os.environ["HEROKU_APPLINK_API_URL"] = "https://fake-url.com"
    os.environ["HEROKU_APPLINK_TOKEN"] = "fake-token"

    # Mock the HTTP request response
    mock_response = {
        "org_id": "00D123",
        "org_domain_url": "https://example.com",
        "user_id": "005123",
        "username": "test@example.com",
        "request_id": "req-12345",
        "access_token": "access-token",
        "api_version": "v1",
        "namespace": "namespace",
    }

    # Use AsyncMock to mock the async function
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        client_context = await get_authorization("DevName")
        assert client_context.org.id == "00D123"
        assert client_context.org.domain_url == "https://example.com"
        assert client_context.org.user.username == "test@example.com"

@pytest.mark.asyncio
async def test_get_authorization_missing_developer_name():
    """Test missing developer name scenario."""
    with pytest.raises(ValueError, match="Developer name must be provided"):
        await get_authorization("")

@pytest.mark.asyncio
async def test_get_authorization_missing_token():
    """Test missing token scenario."""
    os.environ["HEROKU_APPLINK_API_URL"] = "https://fake-url.com"
    # Remove HEROKU_APPLINK_TOKEN from environment
    if "HEROKU_APPLINK_TOKEN" in os.environ:
        del os.environ["HEROKU_APPLINK_TOKEN"]

    # Simulate missing token environment variable
    with pytest.raises(EnvironmentError, match="Missing environment variables for attachment 'HEROKU_APPLINK'"):
        await get_authorization("DevName")

@pytest.mark.asyncio
async def test_get_authorization_with_invalid_url():
    """Test authorization with an invalid URL."""
    os.environ["HEROKU_APPLINK_API_URL"] = "https://fake-url.com"
    os.environ["HEROKU_APPLINK_TOKEN"] = "fake-token"

    mock_response = {
        "org_id": "00D123",
        "org_domain_url": "https://example.com",
        "user_id": "005123",
        "username": "test@example.com",
        "request_id": "req-12345",
        "access_token": "access-token",
        "api_version": "v1",
        "namespace": "namespace",
    }

    # Use AsyncMock to mock the async function
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(EnvironmentError, match="Heroku Applink config not found for API URL: https://invalid-url.com"):
            await get_authorization("DevName", "https://invalid-url.com")

@pytest.mark.asyncio
async def test_get_authorization_runtime_error_in_response():
    """Test runtime error in response from API."""
    os.environ["HEROKU_APPLINK_API_URL"] = "https://fake-url.com"
    os.environ["HEROKU_APPLINK_TOKEN"] = "fake-token"

    mock_response = {
        "message": "Authorization error"
    }

    # Use AsyncMock to mock the async function
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(RuntimeError, match="Authorization request failed: Authorization error"):
            await get_authorization("DevName")

@pytest.mark.asyncio
async def test_resolve_addon_config_by_attachment():
    """Test resolve_addon_config_by_attachment function."""
    os.environ["HEROKU_APPLINK_API_URL"] = "https://fake-url.com"
    os.environ["HEROKU_APPLINK_TOKEN"] = "fake-token"

    config = resolve_addon_config_by_attachment("HEROKU_APPLINK")
    assert config["api_url"] == "https://fake-url.com"
    assert config["token"] == "fake-token"

    with pytest.raises(EnvironmentError, match="Missing environment variables for attachment 'INVALID_ATTACHMENT'"):
        resolve_addon_config_by_attachment("INVALID_ATTACHMENT")

@pytest.mark.asyncio
async def test_resolve_addon_config_by_url():
    """Test resolve_addon_config_by_url function."""
    os.environ["FAKE_API_URL"] = "https://fake-url.com"
    os.environ["FAKE_TOKEN"] = "fake-token"

    config = resolve_addon_config_by_url("https://fake-url.com")
    assert config["api_url"] == "https://fake-url.com"
    assert config["token"] == "fake-token"

    with pytest.raises(EnvironmentError, match="Heroku Applink config not found for API URL: https://invalid-url.com"):
        resolve_addon_config_by_url("https://invalid-url.com")

@pytest.mark.parametrize("url,expected", [
    ("https://valid.url", True),
    ("invalid-url", False),
    ("ftp://ftp.url", True),
])
def test_validate_url(url, expected):
    """Test validate_url function."""
    assert validate_url(url) == expected
