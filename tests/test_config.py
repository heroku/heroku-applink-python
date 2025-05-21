import pytest
import aiohttp

from heroku_applink.config import Config

@pytest.mark.asyncio
async def test_config_default():
    config = Config.default()
    assert config.session is not None
    assert config.session.timeout == aiohttp.ClientTimeout(total=5)

@pytest.mark.asyncio
async def test_config_client_session():
    session = aiohttp.ClientSession(
        cookie_jar=aiohttp.DummyCookieJar(),
        timeout=aiohttp.ClientTimeout(total=5),
    )
    config = Config(session=session)
    assert config.session is not None
    assert config.session.timeout == aiohttp.ClientTimeout(total=5)
