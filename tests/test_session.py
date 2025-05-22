import pytest

from aioresponses import aioresponses

from heroku_applink.config import Config
from heroku_applink.session import Session

@pytest.fixture
def config():
    return Config(
        request_timeout=5.0,
        connect_timeout=1.0,
        socket_connect=1.0,
        socket_read=1.0
    )

@pytest.fixture
def session(config):
    return Session(config)

def test_session_init(config):
    session = Session(config)
    assert isinstance(session, Session)
    assert session._config == config
    assert session._session is None

@pytest.mark.asyncio
async def test_session_request_get(session):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        response = await session.request("GET", "https://example.com")
        assert response.status == 200
        data = await response.json()
        assert data == {'key': 'value'}

@pytest.mark.asyncio
async def test_session_request_post(session):
    with aioresponses() as m:
        m.post(
            'https://example.com',
            status=201,
            payload={'id': '123'}
        )

        response = await session.request(
            "POST",
            "https://example.com",
            data={'name': 'test'}
        )
        assert response.status == 201
        data = await response.json()
        assert data == {'id': '123'}

@pytest.mark.asyncio
async def test_session_request_with_headers(session):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        headers = {'Authorization': 'Bearer token'}
        response = await session.request(
            "GET",
            "https://example.com",
            headers=headers
        )
        assert response.status == 200

@pytest.mark.asyncio
async def test_session_request_error(session):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=500,
            payload={'error': 'Internal Server Error'}
        )

        response = await session.request("GET", "https://example.com")
        assert response.status == 500
        data = await response.json()
        assert data == {'error': 'Internal Server Error'}

@pytest.mark.asyncio
async def test_session_close(session):
    # First request creates the session
    with aioresponses() as m:
        m.get('https://example.com', status=200)
        await session.request("GET", "https://example.com")
        assert session._session is not None

    # Close the session
    await session.close()
    assert session._session is None

@pytest.mark.asyncio
async def test_session_reuse(session):
    with aioresponses() as m:
        m.get('https://example.com', status=200, repeat=True)

        # First request
        response1 = await session.request("GET", "https://example.com")
        assert response1.status == 200
        session1 = session._session

        # Second request should reuse the same session
        response2 = await session.request("GET", "https://example.com")
        assert response2.status == 200
        assert session._session is session1

@pytest.mark.asyncio
async def test_session_custom_timeout(session):
    with aioresponses() as m:
        m.get(
            'https://example.com',
            status=200,
            payload={'key': 'value'}
        )

        response = await session.request(
            "GET",
            "https://example.com",
            timeout=10.0
        )
        assert response.status == 200
        data = await response.json()
        assert data == {'key': 'value'}

@pytest.mark.asyncio
async def test_session_multiple_requests(session):
    with aioresponses() as m:
        m.get('https://example.com/1', status=200, payload={'id': '1'})
        m.get('https://example.com/2', status=200, payload={'id': '2'})
        m.get('https://example.com/3', status=200, payload={'id': '3'})

        # Make multiple requests
        responses = []
        for i in range(1, 4):
            response = await session.request(f"GET", f"https://example.com/{i}")
            data = await response.json()
            responses.append(data)

        assert responses == [
            {'id': '1'},
            {'id': '2'},
            {'id': '3'}
        ]
