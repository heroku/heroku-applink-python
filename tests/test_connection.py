import pytest

from aioresponses import aioresponses

from heroku_applink.config import Config
from heroku_applink.connection import Connection

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

        response = await connection.request("GET", "https://example.com")
        assert response.status == 500
        data = await response.json()
        assert data == {'error': 'Internal Server Error'}

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
