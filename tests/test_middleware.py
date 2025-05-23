import pytest

from heroku_applink.middleware import (
    IntegrationWsgiMiddleware,
    IntegrationAsgiMiddleware,
    client_context,
)
from heroku_applink.context import ClientContext, Org, User
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def mock_client_context():
    return ClientContext(
        org=Org(
            id="00DJS0000000123ABC",
            domain_url="https://example-domain-url.my.salesforce.com",
            user=User(id="005JS000000H123", username="user@example.tld"),
        ),
        request_id="test-request-id",
        access_token="test-access-token",
        api_version="v1",
        namespace="test-namespace",
        data_api=Mock(),
    )

def test_wsgi_middleware_initialization():
    """Test that the WSGI middleware can be initialized."""
    mock_get_response = Mock()
    middleware = IntegrationWsgiMiddleware(mock_get_response)
    assert middleware.get_response == mock_get_response

def test_wsgi_middleware_call(mock_client_context):
    """Test the WSGI middleware call method."""
    mock_get_response = Mock(return_value="response")
    middleware = IntegrationWsgiMiddleware(mock_get_response)

    mock_request = Mock()
    mock_request.headers = {"x-client-context": "dummy-header"}

    with patch("heroku_applink.middleware.ClientContext.from_header", return_value=mock_client_context):
        response = middleware(mock_request)
        assert response == "response"
        assert client_context.get() == mock_client_context

@pytest.mark.asyncio
async def test_asgi_middleware_initialization():
    """Test that the ASGI middleware can be initialized."""
    mock_app = AsyncMock()
    middleware = IntegrationAsgiMiddleware(mock_app)
    assert middleware.app == mock_app

@pytest.mark.asyncio
async def test_asgi_middleware_call(mock_client_context):
    """Test the ASGI middleware call method."""
    mock_app = AsyncMock()
    middleware = IntegrationAsgiMiddleware(mock_app)

    scope = {
        "type": "http",
        "headers": [(b"x-client-context", b"dummy-header")],
    }
    receive = Mock()
    send = Mock()

    with patch("heroku_applink.middleware.ClientContext.from_header", return_value=mock_client_context):
        await middleware(scope, receive, send)
        assert client_context.get() == mock_client_context
        assert scope["client-context"] == mock_client_context
        mock_app.assert_called_once_with(scope, receive, send)
