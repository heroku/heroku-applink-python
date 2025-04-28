import pytest
from heroku_applink.middleware import (
    from_request,
    IntegrationWsgiMiddleware,
    IntegrationAsgiMiddleware,
    client_context,
)
from heroku_applink.context import ClientContext

class MockRequest:
    def __init__(self, headers=None):
        self.headers = headers or {}

def test_from_request_valid_header():
    headers = {"x-client-context": "test-context"}
    request = MockRequest(headers)
    context = from_request(request)
    assert isinstance(context, ClientContext)

def test_from_request_missing_header():
    request = MockRequest()
    with pytest.raises(ValueError, match="x-client-context not set"):
        from_request(request)

def test_wsgi_middleware():
    def mock_get_response(request):
        return "response"

    middleware = IntegrationWsgiMiddleware(mock_get_response)
    headers = {"x-client-context": "test-context"}
    request = MockRequest(headers)
    
    response = middleware(request)
    assert response == "response"
    assert isinstance(client_context.get(), ClientContext)

@pytest.mark.asyncio
async def test_asgi_middleware():
    async def mock_app(scope, receive, send):
        assert "client-context" in scope
        assert isinstance(scope["client-context"], ClientContext)
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"response"})

    middleware = IntegrationAsgiMiddleware(mock_app)
    scope = {
        "type": "http",
        "headers": [(b"x-client-context", b"test-context")]
    }
    
    async def mock_receive():
        return {"type": "http.request"}
    
    async def mock_send(message):
        if message["type"] == "http.response.start":
            assert message["status"] == 200
        elif message["type"] == "http.response.body":
            assert message["body"] == b"response"

    await middleware(scope, mock_receive, mock_send)
    assert isinstance(client_context.get(), ClientContext) 