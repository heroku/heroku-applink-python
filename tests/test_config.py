import pytest
import aiohttp

from heroku_applink.config import Config

@pytest.mark.asyncio
async def test_config_default():
    config = Config.default()

    assert config.request_timeout == 5
    assert config.connect_timeout is None
    assert config.socket_connect is None
    assert config.socket_read is None

@pytest.mark.asyncio
async def test_config_client_session():
    config = Config(request_timeout=10)

    assert config.request_timeout == 10
    assert config.connect_timeout is None
    assert config.socket_connect is None
    assert config.socket_read is None
