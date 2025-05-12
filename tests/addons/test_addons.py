import pytest
from unittest.mock import AsyncMock, patch
from heroku_applink.addons.heroku_applink import get_authorization


@pytest.mark.asyncio
async def test_get_authorization_success(monkeypatch):
    """Test successful authorization request."""
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://fake-url.com")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "fake-token")

    mock_response = {
        "org_id": "00D123",
        "org_domain_url": "https://example.com",
        "user_id": "005123",
        "username": "test@example.com"
    }

    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        org = await get_authorization("DevName")
        assert org.id == "00D123"
        assert org.domain_url == "https://example.com"
        assert org.user.username == "test@example.com"


@pytest.mark.asyncio
async def test_get_authorization_with_invalid_url(monkeypatch):
    """Test authorization with an invalid URL."""
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "http://invalid-url")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "fake-token")

    # Mock the request method to simulate an exception (invalid URL)
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(side_effect=Exception("Invalid URL"))):
        with pytest.raises(RuntimeError, match="Failed to fetch authorization"):
            await get_authorization("DevName")


@pytest.mark.asyncio
async def test_get_authorization_missing_token(monkeypatch):
    """Test missing token scenario."""
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://fake-url.com")

    # Mock request method
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock()):
        # Ensure that a missing token raises an EnvironmentError
        with pytest.raises(EnvironmentError, match="Heroku Applink endpoint or token not configured"):
            await get_authorization("DevName")


@pytest.mark.asyncio
async def test_get_authorization_with_attachment_name(monkeypatch):
    """Test authorization with attachment name passed."""
    monkeypatch.setenv("HEROKU_APPLINK_FAKE_API_URL", "https://fake-url.com")
    monkeypatch.setenv("HEROKU_APPLINK_FAKE_TOKEN", "fake-token")

    mock_response = {
        "org_id": "00D123",
        "org_domain_url": "https://example.com",
        "user_id": "005123",
        "username": "test@example.com"
    }

    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        org = await get_authorization("DevName", "fake")
        assert org.id == "00D123"
        assert org.domain_url == "https://example.com"
        assert org.user.username == "test@example.com"


@pytest.mark.asyncio
async def test_get_authorization_with_invalid_attachment_name(monkeypatch):
    """Test authorization with an invalid attachment name."""
    monkeypatch.setenv("HEROKU_APPLINK_FAKE_API_URL", "")
    monkeypatch.setenv("HEROKU_APPLINK_FAKE_TOKEN", "")

    # Mock the request method to simulate a failure in environment variable retrieval
    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock()):
        with pytest.raises(EnvironmentError, match="Missing environment variables for attachment 'fake'"):
            await get_authorization("DevName", "fake")


@pytest.mark.asyncio
async def test_get_authorization_with_http_url(monkeypatch):
    """Test authorization with a URL-based attachment."""
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "fake-token")

    mock_response = {
        "org_id": "00D123",
        "org_domain_url": "https://example.com",
        "user_id": "005123",
        "username": "test@example.com"
    }

    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        org = await get_authorization("DevName", "http://fake-url.com")
        assert org.id == "00D123"
        assert org.domain_url == "https://example.com"
        assert org.user.username == "test@example.com"


@pytest.mark.asyncio
async def test_get_authorization_missing_url_and_token(monkeypatch):
    """Test missing URL and token scenario."""
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "")

    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock()):
        with pytest.raises(EnvironmentError, match="Heroku Applink endpoint or token not configured"):
            await get_authorization("DevName")

@pytest.mark.asyncio
async def test_get_authorization_missing_developer_name(monkeypatch):
    """Test authorization with missing developer name."""
    # Assert that ValueError is raised when developer_name is not provided
    with pytest.raises(ValueError, match="Developer name must be provided"):
        await get_authorization("", "fake")

@pytest.mark.asyncio
async def test_get_authorization_runtime_error_in_response(monkeypatch):
    """Test authorization where the response has an error message."""
    # Set environment variables for the test
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://fake-url.com")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "fake-token")

    # Mock the request method to simulate an error message in the response
    mock_response = {"message": "Invalid organization name"}

    with patch("heroku_applink.utils.http_request.HttpRequestUtil.request", new=AsyncMock(return_value=mock_response)):
        # Assert that a RuntimeError is raised when the response contains an error message
        with pytest.raises(RuntimeError, match="Invalid organization name"):
            await get_authorization("DevName")
