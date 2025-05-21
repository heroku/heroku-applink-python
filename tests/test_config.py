import pytest
import aiohttp

from heroku_applink.config import Config

@pytest.mark.asyncio
async def test_config_default():
    config = Config.default()
    assert config.session is not None
    assert config.session.timeout == aiohttp.ClientTimeout(total=5)
