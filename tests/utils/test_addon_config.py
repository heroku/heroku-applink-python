import pytest
import os

from heroku_applink.utils.addon_config import (
    resolve_addon_config_by_attachment_or_color,
    resolve_addon_config_by_url,
)

@pytest.fixture(autouse=True)
def save_restore_env(monkeypatch):
    """Save and restore environment variables for each test."""
    original_env = dict(os.environ)
    # Clear all environment variables before each test
    for key in list(os.environ.keys()):
        monkeypatch.delenv(key, raising=False)
    yield
    # Restore original environment variables after each test
    for key in list(os.environ.keys()):
        if key not in original_env:
            monkeypatch.delenv(key, raising=False)
    for key, value in original_env.items():
        monkeypatch.setenv(key, value)

@pytest.fixture(autouse=True)
def clear_addon_config_cache():
    resolve_addon_config_by_attachment_or_color.cache_clear()
    resolve_addon_config_by_url.cache_clear()

def setup_integration_env(monkeypatch):
    """Setup environment variables simulating multiple attachments."""
    base_url = "https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7"
    token = "integration-token"

    # Direct integration attachment
    monkeypatch.setenv('HEROKU_INTEGRATION_API_URL', base_url)
    monkeypatch.setenv('HEROKU_INTEGRATION_TOKEN', token)

    # Default HEROKU_APPLINK attachment
    monkeypatch.setenv('HEROKU_APPLINK_API_URL', base_url)
    monkeypatch.setenv('HEROKU_APPLINK_TOKEN', token)

    # Color-based attachment
    monkeypatch.setenv('HEROKU_APPLINK_PURPLE_API_URL', base_url)
    monkeypatch.setenv('HEROKU_APPLINK_PURPLE_TOKEN', token)

    # Org name
    monkeypatch.setenv('SALESFORCE_ORG_NAME', 'applink-org')

def test_resolve_by_direct_integration(monkeypatch):
    setup_integration_env(monkeypatch)

    config = resolve_addon_config_by_attachment_or_color('HEROKU_INTEGRATION')
    assert config.api_url == 'https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7'
    assert config.token == 'integration-token'

def test_resolve_by_default_attachment(monkeypatch):
    setup_integration_env(monkeypatch)

    config = resolve_addon_config_by_attachment_or_color('HEROKU_APPLINK')
    assert config.api_url == 'https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7'
    assert config.token == 'integration-token'

def test_resolve_by_url(monkeypatch):
    setup_integration_env(monkeypatch)
    test_url = 'https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7'

    config = resolve_addon_config_by_url(test_url)
    assert config.api_url == test_url
    assert config.token == 'integration-token'

def test_resolve_by_color(monkeypatch):
    setup_integration_env(monkeypatch)

    config = resolve_addon_config_by_attachment_or_color('purple')
    assert config.api_url == 'https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7'
    assert config.token == 'integration-token'

def test_resolve_by_nonexistent_attachment(monkeypatch):
    setup_integration_env(monkeypatch)

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_attachment_or_color("APPLINKN'T")
    assert "Heroku Applink config not found under attachment or color APPLINKN'T" in str(exc_info.value)

def test_resolve_by_nonexistent_color(monkeypatch):
    setup_integration_env(monkeypatch)

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_attachment_or_color("purplee")
    assert "Heroku Applink config not found under attachment or color purplee" in str(exc_info.value)

def test_resolve_by_custom_addon_name_failure(monkeypatch):
    setup_integration_env(monkeypatch)
    monkeypatch.setenv('HEROKU_APPLINK_ADDON_NAME', 'FAKE_HEROKU_APPLINK')

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_attachment_or_color('purple')
    assert "Heroku Applink config not found under attachment or color purple" in str(exc_info.value)

def test_resolve_by_custom_addon_name_success(monkeypatch):
    setup_integration_env(monkeypatch)
    monkeypatch.setenv('HEROKU_APPLINK_ADDON_NAME', 'HEROKU_APPLINK')

    config = resolve_addon_config_by_attachment_or_color('purple')
    assert config.api_url == 'https://heroku-integration.heroku.com/addons/c694c5b3-7e07-4eb1-bb76-caf106a25bb7'
    assert config.token == 'integration-token'

def test_resolve_by_attachment(monkeypatch):
    # Set direct attachment env vars
    monkeypatch.setenv('HEROKU_APPLINK_API_URL', 'https://api.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_TOKEN', 'default-token')

    config = resolve_addon_config_by_attachment_or_color('HEROKU_APPLINK')
    assert config.api_url == 'https://api.example.com'
    assert config.token == 'default-token'

def test_resolve_by_attachment_case_insensitive(monkeypatch):
    # Set direct attachment env vars
    monkeypatch.setenv('HEROKU_APPLINK_API_URL', 'https://api.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_TOKEN', 'default-token')

    config = resolve_addon_config_by_attachment_or_color('heroku_applink')
    assert config.api_url == 'https://api.example.com'
    assert config.token == 'default-token'

def test_resolve_by_color_with_custom_addon_name(monkeypatch):
    # Set custom addon name and color-specific env vars
    monkeypatch.setenv('HEROKU_APPLINK_ADDON_NAME', 'HEROKU_APPLINK_STAGING')
    monkeypatch.setenv('HEROKU_APPLINK_STAGING_PURPLE_API_URL', 'https://api.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_STAGING_PURPLE_TOKEN', 'default-token')

    config = resolve_addon_config_by_attachment_or_color('purple')
    assert config.api_url == 'https://api.example.com'
    assert config.token == 'default-token'

def test_resolve_by_nonexistent_attachment_with_fallback(monkeypatch):
    # Test that a nonexistent attachment name still works if the fallback exists
    # First, ensure direct attachment vars don't exist
    monkeypatch.delenv('MYADDON_API_URL', raising=False)
    monkeypatch.delenv('MYADDON_TOKEN', raising=False)

    # Set the fallback vars
    monkeypatch.setenv('HEROKU_APPLINK_MYADDON_API_URL', 'https://api.example.com')
    monkeypatch.setenv('HEROKU_APPLINK_MYADDON_TOKEN', 'fallback-token')

    config = resolve_addon_config_by_attachment_or_color('myaddon')
    assert config.api_url == 'https://api.example.com'
    assert config.token == 'fallback-token'

def test_missing_api_url(monkeypatch):
    # Set only token, missing API_URL
    monkeypatch.setenv('HEROKU_APPLINK_TOKEN', 'token')
    # HEROKU_APPLINK_API_URL intentionally not set

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_attachment_or_color('HEROKU_APPLINK')
    assert "Heroku Applink config not found under attachment or color HEROKU_APPLINK" in str(exc_info.value)

def test_missing_token(monkeypatch):
    # Set only API_URL, missing token
    monkeypatch.setenv('HEROKU_APPLINK_API_URL', 'https://api.example.com')
    # HEROKU_APPLINK_TOKEN intentionally not set

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_attachment_or_color('HEROKU_APPLINK')
    assert "Heroku Applink config not found under attachment or color HEROKU_APPLINK" in str(exc_info.value)

def test_resolve_by_url_case_insensitive(monkeypatch):
    test_url = "https://api.example.com"
    monkeypatch.setenv('HEROKU_APPLINK_API_URL', test_url)
    monkeypatch.setenv('HEROKU_APPLINK_TOKEN', 'test-token')

    config = resolve_addon_config_by_url(test_url.upper())
    assert config.api_url == test_url
    assert config.token == 'test-token'

def test_resolve_by_url_not_found(monkeypatch):
    test_url = "https://nonexistent.example.com"

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_url(test_url)
    assert f"Heroku Applink config not found for API URL: {test_url}" in str(exc_info.value)

def test_resolve_by_url_missing_token(monkeypatch):
    test_url = "https://api.example.com"
    monkeypatch.setenv('SOME_API_URL', test_url)
    # SOME_TOKEN intentionally not set

    with pytest.raises(ValueError) as exc_info:
        resolve_addon_config_by_url(test_url)
    assert f"Heroku Applink token not found for API URL: {test_url}" in str(exc_info.value)
