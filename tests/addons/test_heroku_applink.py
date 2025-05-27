import pytest
import urllib.parse
from typing import Dict, Any

# import heroku_applink.addons.heroku_applink as module

from heroku_applink.context import ClientContext, Org, User, DataAPI

# Use pytest-asyncio for testing async functions
pytest_plugins = ("pytest_asyncio",)

# A sample valid response payload from the add-on
VALID_RESPONSE: Dict[str, Any] = {
    "org_id": "00DTEST123",
    "org_domain_url": "https://example.my.salesforce.com/",
    "user_id": "005TEST456",
    "username": "user@example.com",
    "request_id": "REQ-789",
    "access_token": "TOKEN_ABC",
    "api_version": "v52.0",
    "namespace": "testns",
}


class DummyError(Exception):
    pass


@pytest.fixture(autouse=True)
def stub_config_and_request(monkeypatch):
    """
    By default:
    - resolve_addon_config_by_attachment_or_color returns a simple config
    - resolve_addon_config_by_url returns a simple config
    - http_request_util.request returns VALID_RESPONSE
    """
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test")
    monkeypatch.setenv("HEROKU_APPLINK_TOKEN", "TOKEN")

    monkeypatch.setenv("ONE_API_URL", "https://one.test")
    monkeypatch.setenv("ONE_TOKEN", "ONE_TOKEN")

    async def fake_request(url, opts):
        return VALID_RESPONSE.copy()

    monkeypatch.setattr(
        module, "resolve_addon_config_by_attachment_or_color", lambda x: {
            "api_url": "https://api.test/",
            "token": "TOKEN"
        }
    )
    monkeypatch.setattr(
        module, "resolve_addon_config_by_url", lambda x: {
            "api_url": "https://one.test",
            "token": "ONE_TOKEN"
        }
    )
    monkeypatch.setattr(
        module.http_request_util, "request", fake_request
    )

    yield


@pytest.mark.asyncio
async def test_missing_developer_name():
    with pytest.raises(ValueError) as exc:
        await module.get_authorization("", None)
    assert "Developer name must be provided" in str(exc.value)


@pytest.mark.asyncio
async def test_attachment_based_success(monkeypatch):
    # Call without trailing slash base, ensure rstrip
    monkeypatch.setenv("HEROKU_APPLINK_API_URL", "https://api.test/")
    ctx = await module.get_authorization("devName", None)

    # Ensure ClientContext is populated
    assert isinstance(ctx, ClientContext)
    assert isinstance(ctx.org, Org)
    assert ctx.org.id == VALID_RESPONSE["org_id"]
    assert ctx.org.domain_url == VALID_RESPONSE["org_domain_url"]
    assert isinstance(ctx.org.user, User)
    assert ctx.org.user.id == VALID_RESPONSE["user_id"]
    assert ctx.request_id == VALID_RESPONSE["request_id"]
    assert ctx.access_token == VALID_RESPONSE["access_token"]
    assert ctx.api_version == VALID_RESPONSE["api_version"]
    assert ctx.namespace == VALID_RESPONSE["namespace"]
    # DataAPI should be initialized with same values
    assert isinstance(ctx.data_api, DataAPI)
    assert ctx.data_api.access_token == VALID_RESPONSE["access_token"]


@pytest.mark.asyncio
async def test_url_based_success(monkeypatch):
    # Passing a URL should route to resolve_addon_config_by_url
    ctx = await module.get_authorization("alice", "https://one.test")
    # Ensure it used the ONE_TOKEN config
    assert ctx.access_token == VALID_RESPONSE["access_token"]
    # Same ClientContext checks
    assert ctx.org.domain_url == VALID_RESPONSE["org_domain_url"]


@pytest.mark.asyncio
async def test_http_error_wrapping(monkeypatch):
    async def raising_request(url, opts):
        raise DummyError("network gone")

    monkeypatch.setattr(
        module.http_request_util, "request", raising_request
    )

    encoded = urllib.parse.urlencode({"org_name": "bob"})
    full_url = f"https://api.test/invocations/authorization?{encoded}"

    with pytest.raises(RuntimeError) as exc:
        await module.get_authorization("bob", None)
    msg = str(exc.value)
    assert "Failed to fetch authorization from" in msg
    assert full_url in msg
    assert "network gone" in msg


@pytest.mark.asyncio
async def test_api_error_message(monkeypatch):
    async def bad_response(url, opts):
        return {"message": "oops, bad"}

    monkeypatch.setattr(
        module.http_request_util, "request", bad_response
    )

    with pytest.raises(RuntimeError) as exc:
        await module.get_authorization("charlie", None)
    assert "Authorization request failed: oops, bad" in str(exc.value)
