import pytest
from unittest.mock import patch, AsyncMock
from heroku_applink.utils.http_request import HttpRequestUtil

@pytest.mark.asyncio
async def test_http_request_success_json():
    """Test successful HTTP request with a JSON response."""
    mock_response = {"key": "value"}
    mock_request = AsyncMock(return_value=mock_response)

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        response = await http_request_util.request("https://fake-url.com", {"method": "GET"})
        assert response == mock_response
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"})

@pytest.mark.asyncio
async def test_http_request_success_no_json():
    """Test successful HTTP request with non-JSON response."""
    mock_response = b"binary data"
    mock_request = AsyncMock(return_value=mock_response)

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        response = await http_request_util.request("https://fake-url.com", {"method": "GET"}, return_json=False)
        assert response == mock_response
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"}, return_json=False)

@pytest.mark.asyncio
async def test_http_request_network_error():
    """Test network error when making the request."""
    mock_request = AsyncMock(side_effect=Exception("Network Error"))

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        with pytest.raises(Exception, match="Network Error"):
            await http_request_util.request("https://fake-url.com", {"method": "GET"})
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"})

@pytest.mark.asyncio
async def test_http_request_missing_method():
    """Test missing method in options (defaults to GET)."""
    mock_response = {"key": "value"}
    mock_request = AsyncMock(return_value=mock_response)

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        # No method provided, defaults to GET
        response = await http_request_util.request("https://fake-url.com", {"headers": {}})
        assert response == mock_response
        mock_request.assert_called_once_with("https://fake-url.com", {"headers": {}})

@pytest.mark.asyncio
async def test_http_request_missing_headers():
    """Test missing headers in options."""
    mock_response = {"key": "value"}
    mock_request = AsyncMock(return_value=mock_response)

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        response = await http_request_util.request("https://fake-url.com", {"method": "GET"})
        assert response == mock_response
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"})

@pytest.mark.asyncio
async def test_http_request_invalid_url():
    """Test invalid URL handling."""
    mock_request = AsyncMock(side_effect=ValueError("Invalid URL"))

    http_request_util = HttpRequestUtil()

    with patch.object(HttpRequestUtil, 'request', mock_request):
        with pytest.raises(ValueError, match="Invalid URL"):
            await http_request_util.request("invalid-url", {"method": "GET"})
        mock_request.assert_called_once_with("invalid-url", {"method": "GET"})
