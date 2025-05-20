import pytest

from heroku_applink.utils.addon_config import (
    resolve_addon_config_by_attachment_or_color,
    resolve_addon_config_by_url,
)


def test_resolve_by_attachment(monkeypatch):
    # Set direct attachment env vars
    monkeypatch.setenv('MYADDON_API_URL', 'https://api.example.com')
    monkeypatch.setenv('MYADDON_TOKEN', 'secret-token')

    config = resolve_addon_config_by_attachment_or_color('myaddon')
    assert config['api_url'] == 'https://api.example.com'
    assert config['token'] == 'secret-token'


def test_resolve_by_color_fallback(monkeypatch):
    # Remove direct and set fallback under HEROKU_APPLINK
    monkeypatch.delenv('COLOR_API_URL', raising=False)
    monkeypatch.delenv('COLOR_TOKEN', raising=False)
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_API_URL', 'https://color.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_COLOR_TOKEN', 'color-token')

    config = resolve_addon_config_by_attachment_or_color('color')
    assert config['api_url'] == 'https://color.example.com'
    assert config['token'] == 'color-token'


def test_resolve_missing_attachment_and_fallback(monkeypatch):
    # Ensure neither direct nor fallback exist
    monkeypatch.delenv('NADA_API_URL', raising=False)
    monkeypatch.delenv('NADA_TOKEN', raising=False)
    monkeypatch.delenv('HEROKU_APPLINK_NADA_API_URL', raising=False)
    monkeypatch.delenv('HEROKU_APPLINK_NADA_TOKEN', raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        resolve_addon_config_by_attachment_or_color('nada')
    message = str(exc_info.value)
    assert "Heroku Applink config not found for 'nada'" in message


def test_resolve_by_url(monkeypatch):
    # Set URL env var and corresponding token
    monkeypatch.setenv('EXAMPLE_API_URL', 'https://api.test.com')
    monkeypatch.setenv('EXAMPLE_TOKEN', 'url-token')

    config = resolve_addon_config_by_url('https://api.test.com')
    assert config['api_url'] == 'https://api.test.com'
    assert config['token'] == 'url-token'


def test_resolve_by_url_case_insensitive(monkeypatch):
    # URL matching should be case-insensitive
    monkeypatch.setenv('CASE_API_URL', 'https://Case.Example.COM')
    monkeypatch.setenv('CASE_TOKEN', 'case-token')

    config = resolve_addon_config_by_url('https://case.example.com')
    assert config['api_url'] == 'https://Case.Example.COM'
    assert config['token'] == 'case-token'


def test_resolve_by_url_missing(monkeypatch):
    monkeypatch.delenv('MISSING_API_URL', raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        resolve_addon_config_by_url('https://doesnotexist')
    assert 'Heroku Applink config not found for API URL' in str(exc_info.value)
