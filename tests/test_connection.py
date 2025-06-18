import pytest
import aiohttp
import uuid

from aioresponses import aioresponses
from yarl import URL

from heroku_applink.config import Config
from heroku_applink.connection import Connection, set_request_id

@pytest.fixture
def config():
    return Config(
        request_timeout=5.0,
        connect_timeout=1.0,
        socket_connect=1.0,
        socket_read=1.0
    )

@pytest.fixture
def connection(config):
    return Connection(config)

def test_connection_init(config):
    connection = Connection(config)
    assert isinstance(connection, Connection)
    assert connection._config == config

@pytest.mark.asyncio
async def test_connection_request_get(connection):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        response = await connection.request("GET", "https://example.com")

        assert response.status == 200
        data = await response.json()
        assert data == {'key': 'value'}

@pytest.mark.asyncio
async def test_connection_request_post(connection):
    with aioresponses() as m:
        m.post(
            'https://example.com',
            status=201,
            payload={'id': '123'}
        )

        response = await connection.request(
            "POST",
            "https://example.com",
            data={'name': 'test'}
        )
        assert response.status == 201
        data = await response.json()
        assert data == {'id': '123'}

@pytest.mark.asyncio
async def test_connection_request_with_headers(connection):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        headers = {'Authorization': 'Bearer token'}
        response = await connection.request(
            "GET",
            "https://example.com",
            headers=headers
        )
        assert response.status == 200

@pytest.mark.asyncio
async def test_connection_request_error(connection):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=500,
            payload={'error': 'Internal Server Error'}
        )

        with pytest.raises(aiohttp.ClientResponseError) as exc_info:
            await connection.request("GET", "https://example.com")

        assert exc_info.value.status == 500

@pytest.mark.asyncio
async def test_connection_close(connection):
    # First request creates the connection
    with aioresponses() as m:
        m.get('https://example.com', status=200)
        await connection.request("GET", "https://example.com")
        assert connection._session is not None

    # Close the session
    await connection.close()
    assert connection._session is None

@pytest.mark.asyncio
async def test_connection_reuse(connection):
    with aioresponses() as m:
        m.get('https://example.com', status=200, repeat=True)

        # First request
        response1 = await connection.request("GET", "https://example.com")
        assert response1.status == 200
        session1 = connection._session

        # Second request should reuse the same session
        response2 = await connection.request("GET", "https://example.com")
        assert response2.status == 200
        assert connection._session is session1

@pytest.mark.asyncio
async def test_connection_custom_timeout(connection):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        response = await connection.request(
            "GET",
            "https://example.com",
            timeout=10.0
        )
        assert response.status == 200
        data = await response.json()
        assert data == {'key': 'value'}

@pytest.mark.asyncio
async def test_connection_multiple_requests(connection):
    with aioresponses() as m:
        m.get('https://example.com/1', status=200, payload={'id': '1'})
        m.get('https://example.com/2', status=200, payload={'id': '2'})
        m.get('https://example.com/3', status=200, payload={'id': '3'})

        # Make multiple requests
        responses = []
        for i in range(1, 4):
            response = await connection.request("GET", f"https://example.com/{i}")
            data = await response.json()
            responses.append(data)

        assert responses == [
            {'id': '1'},
            {'id': '2'},
            {'id': '3'}
        ]

@pytest.mark.asyncio
async def test_connection_sets_request_id_header_when_contextvar_not_set(connection):
    with aioresponses() as m:
        m.get('https://example.com', status=200, payload={'success': True})

        response = await connection.request("GET", "https://example.com")

        assert response.status == 200

        request_kwargs = m.requests[('GET', URL('https://example.com'))][0].kwargs
        headers = request_kwargs['headers']
        assert 'X-Request-Id' in headers

        request_id_value = headers['X-Request-Id']
        assert isinstance(request_id_value, str)

        uuid.UUID(request_id_value)

@pytest.mark.asyncio
async def test_connection_uses_contextvar_request_id_when_set(connection):
    test_request_id = "test-request-id-12345"

    with aioresponses() as m:
        m.get('https://example.com', status=200, payload={'success': True})

        set_request_id(test_request_id)

        response = await connection.request("GET", "https://example.com")

        assert response.status == 200

        request_kwargs = m.requests[('GET', URL('https://example.com'))][0].kwargs
        headers = request_kwargs['headers']
        assert headers['X-Request-Id'] == test_request_id

@pytest.mark.asyncio
async def test_connection_request_id_header_with_custom_headers(connection):
    test_request_id = "custom-request-id-67890"
    custom_headers = {'Authorization': 'Bearer token', 'Content-Type': 'application/json'}

    with aioresponses() as m:
        m.post('https://example.com', status=200, payload={'success': True})

        set_request_id(test_request_id)

        response = await connection.request(
            "POST",
            "https://example.com",
            headers=custom_headers,
            data={'key': 'value'}
        )

        assert response.status == 200

        request_kwargs = m.requests[('POST', URL('https://example.com'))][0].kwargs
        headers = request_kwargs['headers']

        assert headers['Authorization'] == 'Bearer token'
        assert headers['Content-Type'] == 'application/json'
        assert headers['X-Request-Id'] == test_request_id

@pytest.mark.asyncio
async def test_connection_request_id_header_override_protection(connection):
    contextvar_request_id = "contextvar-request-id"
    custom_request_id = "custom-header-request-id"

    with aioresponses() as m:
        m.get('https://example.com', status=200, payload={'success': True})

        set_request_id(contextvar_request_id)

        response = await connection.request(
            "GET",
            "https://example.com",
            headers={'X-Request-Id': custom_request_id}
        )

        assert response.status == 200

        request_kwargs = m.requests[('GET', URL('https://example.com'))][0].kwargs
        headers = request_kwargs['headers']
        assert headers['X-Request-Id'] == contextvar_request_id

@pytest.mark.asyncio
async def test_connection_user_agent_header_always_set(connection):
    with aioresponses() as m:
        m.get('https://example.com', status=200, payload={'success': True})

        response = await connection.request("GET", "https://example.com")

        assert response.status == 200

        request_kwargs = m.requests[('GET', URL('https://example.com'))][0].kwargs
        headers = request_kwargs['headers']
        assert headers['User-Agent'] == connection._config.user_agent()

def test_decode_headers_with_empty_input(connection):
    """Test that empty or None headers return an empty dict."""
    assert connection._decode_headers({}) == {}
    assert connection._decode_headers(None) == {}

def test_decode_headers_with_string_values(connection):
    """Test that string headers are returned unchanged."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    }
    assert connection._decode_headers(headers) == headers

def test_decode_headers_with_bytes_keys(connection):
    """Test that byte keys are properly decoded to strings."""
    headers = {
        b"Content-Type": "application/json",
        b"Authorization": "Bearer token"
    }
    decoded = connection._decode_headers(headers)
    assert decoded["Content-Type"] == "application/json"
    assert decoded["Authorization"] == "Bearer token"

def test_decode_headers_with_bytes_values(connection):
    """Test that byte values are properly decoded to strings."""
    headers = {
        "Content-Type": b"application/json",
        "Authorization": b"Bearer token"
    }
    decoded = connection._decode_headers(headers)
    assert decoded["Content-Type"] == "application/json"
    assert decoded["Authorization"] == "Bearer token"

def test_decode_headers_with_mixed_types(connection):
    """Test that mixed byte and string headers are handled correctly."""
    headers = {
        b"Content-Type": b"application/json",
        "Authorization": b"Bearer token",
        b"Accept": "application/json",
        "X-Custom": b"value"
    }
    decoded = connection._decode_headers(headers)
    assert decoded["Content-Type"] == "application/json"
    assert decoded["Authorization"] == "Bearer token"
    assert decoded["Accept"] == "application/json"
    assert decoded["X-Custom"] == "value"

def test_decode_headers_with_non_ascii(connection):
    """Test that non-ASCII characters are properly decoded using latin1."""
    headers = {
        b"X-Custom": b"v\xe4lue",  # 'välue' in latin1
        "X-Other": b"v\xe4lue"
    }
    decoded = connection._decode_headers(headers)
    assert decoded["X-Custom"] == "välue"
    assert decoded["X-Other"] == "välue"
