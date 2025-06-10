import importlib.metadata

from heroku_applink.config import Config

def test_config_default():
    config = Config.default()

    assert config.request_timeout == 5
    assert config.connect_timeout is None
    assert config.socket_connect is None
    assert config.socket_read is None

def test_config_client_timeouts():
    config = Config(request_timeout=10)

    assert config.request_timeout == 10
    assert config.connect_timeout is None
    assert config.socket_connect is None
    assert config.socket_read is None

def test_config_user_agent():
    config = Config.default()

    assert config.user_agent() == f"heroku-applink-python-sdk/{importlib.metadata.version('heroku_applink')}"
