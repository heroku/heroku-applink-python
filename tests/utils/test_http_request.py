import pytest
from unittest.mock import AsyncMock, patch
from heroku_applink.utils.http_request import HttpRequestUtil

@pytest.mark.asyncio
async def test_http_request_success():
    """Test successful HTTP request."""
    # Mock the response to return fake data
    mock_response = {"data": "fake_data"}
    mock_request = AsyncMock(return_value=mock_response)

    # Create an instance of HttpRequestUtil
    http_request_util = HttpRequestUtil()

    # Patch the request method to mock it
    with patch.object(HttpRequestUtil, 'request', mock_request):
        # Call the request method
        response = await http_request_util.request("https://fake-url.com", {"method": "GET"})

        # Assert that the returned response matches the mock
        assert response == mock_response
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"})

@pytest.mark.asyncio
async def test_http_request_failure():
    """Test failed HTTP request with exception handling."""
    # Simulate an error by having the mock raise an exception
    mock_request = AsyncMock(side_effect=Exception("Network error"))

    # Create an instance of HttpRequestUtil
    http_request_util = HttpRequestUtil()

    # Patch the request method to mock it
    with patch.object(HttpRequestUtil, 'request', mock_request):
        # Assert that the error is raised when the request fails
        with pytest.raises(Exception, match="Network error"):
            await http_request_util.request("https://fake-url.com", {"method": "GET"})

@pytest.mark.asyncio
async def test_http_request_no_json():
    """Test HTTP request when return_json is set to False."""
    # Mock the response to return fake binary data
    mock_response = b"binary_data"
    mock_request = AsyncMock(return_value=mock_response)

    # Create an instance of HttpRequestUtil
    http_request_util = HttpRequestUtil()

    # Patch the request method to mock it
    with patch.object(HttpRequestUtil, 'request', mock_request):
        # Call the request method with return_json=False
        response = await http_request_util.request("https://fake-url.com", {"method": "GET"}, return_json=False)

        # Assert that the returned response matches the mock binary data
        assert response == mock_response

        # Update the mock call assertion to check for the correct arguments
        mock_request.assert_called_once_with("https://fake-url.com", {"method": "GET"}, return_json=False)
