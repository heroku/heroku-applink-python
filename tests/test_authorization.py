import pytest

from heroku_applink.config import Config
from heroku_applink.authorization import (
    Authorization,
    _resolve_addon_config_by_attachment_or_color,
    _resolve_addon_config_by_url,
    _is_valid_url,
)

def test_resolve_addon_config_by_url(monkeypatch):
    # Set URL env var and corresponding token
    monkeypatch.setenv('EXAMPLE_API_URL', 'https://api.test.com')
    monkeypatch.setenv('EXAMPLE_TOKEN', 'url-token')

    auth = _resolve_addon_config_by_url("https://api.test.com")

    assert auth is not None
    assert auth.api_url == "https://api.test.com"
    assert auth.token == "url-token"

def test_resolve_by_url_case_insensitive(monkeypatch):
    # URL matching should be case-insensitive
    monkeypatch.setenv('CASE_API_URL', 'https://Case.Example.COM')
    monkeypatch.setenv('CASE_TOKEN', 'case-token')

    auth = _resolve_addon_config_by_url('https://case.example.com')

    assert auth is not None
    assert auth.api_url == 'https://Case.Example.COM'
    assert auth.token == 'case-token'

def test_resolve_by_url_missing(monkeypatch):
    monkeypatch.delenv('MISSING_API_URL', raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        _resolve_addon_config_by_url('https://doesnotexist')
    assert 'Heroku Applink config not found for API URL' in str(exc_info.value)

def test_resolve_addon_config_by_attachment_or_color_direct(monkeypatch):
    # Set direct attachment env vars
    monkeypatch.setenv('MYADDON_API_URL', 'https://api.example.com')
    monkeypatch.setenv('MYADDON_TOKEN', 'secret-token')

    auth = _resolve_addon_config_by_attachment_or_color('myaddon')

    assert auth is not None
    assert auth.api_url == "https://api.example.com"
    assert auth.token == "secret-token"

def test_resolve_by_color_fallback(monkeypatch):
    # Remove direct and set fallback under HEROKU_APPLINK
    monkeypatch.delenv('COLOR_API_URL', raising=False)
    monkeypatch.delenv('COLOR_TOKEN', raising=False)
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_API_URL', 'https://color.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_TOKEN', 'color-token')

    auth = _resolve_addon_config_by_attachment_or_color("color")

    assert auth is not None
    assert auth.api_url == "https://color.example.com"
    assert auth.token == "color-token"

def test_is_valid_url():
    assert _is_valid_url("https://api.test.com") is True
    assert _is_valid_url("http://api.test.com") is True
    assert _is_valid_url("api.test.com") is False
    assert _is_valid_url("test") is False
    assert _is_valid_url("https://") is False
    assert _is_valid_url("https://api.test.com/") is True
