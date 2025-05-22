import pytest

from heroku_applink.config import Config
from heroku_applink.session import Session

def test_session_init():
    session = Session(Config.default())

    assert isinstance(session, Session)
