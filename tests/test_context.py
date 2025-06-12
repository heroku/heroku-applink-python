import base64
import json
import pytest

from heroku_applink.config import Config
from heroku_applink.context import User, Org, ClientContext
from heroku_applink.connection import Connection

class FakeDataAPI:
    """Fake DataAPI class for testing without real dependencies."""
    def __init__(self, org_domain_url, api_version, access_token, connection):
        self.org_domain_url = org_domain_url
        self.api_version = api_version
        self.access_token = access_token
        self.connection = connection

@pytest.fixture(autouse=True)
def patch_data_api(monkeypatch):
    # Patch heroku_applink.context.DataAPI with our fake
    monkeypatch.setattr("heroku_applink.context.DataAPI", FakeDataAPI)

def test_user_creation():
    user = User(id="005JS000000H123", username="user@example.tld")
    assert user.id == "005JS000000H123"
    assert user.username == "user@example.tld"

def test_org_creation():
    user = User(id="005JS000000H123", username="user@example.tld")
    org = Org(id="00DJS0000000123ABC", domain_url="https://example-domain.my.salesforce.com", user=user)
    assert org.id == "00DJS0000000123ABC"
    assert org.domain_url.startswith("https://")
    assert isinstance(org.user, User)

def test_client_context_creation():
    user = User(id="005JS000000H123", username="user@example.tld")
    org = Org(id="00DJS0000000123ABC", domain_url="https://example-domain.my.salesforce.com", user=user)
    ctx = ClientContext(
        org=org,
        data_api=FakeDataAPI(
            org_domain_url=org.domain_url,
            api_version="v57.0",
            access_token="fake_token",
            connection=Connection(Config.default()),
        ),
        request_id="req-123",
        access_token="fake_token",
        api_version="v57.0",
        namespace="mynamespace",
    )
    assert ctx.org.id == "00DJS0000000123ABC"
    assert ctx.data_api.api_version == "v57.0"
    assert ctx.request_id == "req-123"

def test_client_context_from_header():
    payload = {
        "orgId": "00DJS0000000123ABC",
        "orgDomainUrl": "https://example-domain.my.salesforce.com",
        "userContext": {
            "userId": "005JS000000H123",
            "username": "user@example.tld",
        },
        "requestId": "req-456",
        "accessToken": "access-token-xyz",
        "apiVersion": "v57.0",
        "namespace": "ns",
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    connection = Connection(Config.default())
    ctx = ClientContext.from_header(encoded, connection)

    assert ctx.org.id == "00DJS0000000123ABC"
    assert ctx.org.user.username == "user@example.tld"
    assert ctx.request_id == "req-456"
    assert ctx.access_token == "access-token-xyz"
    assert ctx.api_version == "v57.0"
    assert ctx.namespace == "ns"

def test_client_context_from_header_invalid():
    # Provide bad Base64 encoded string
    with pytest.raises(Exception):
        ClientContext.from_header("not-valid-base64")

def test_client_context_from_header_with_null_namespace():
    payload = {
        "orgId": "00DJS0000000123ABC",
        "orgDomainUrl": "https://example-domain.my.salesforce.com",
        "userContext": {
            "userId": "005JS000000H123",
            "username": "user@example.tld",
        },
        "requestId": "req-456",
        "accessToken": "access-token-xyz",
        "apiVersion": "v57.0",
        "namespace": None,  # Explicitly set to None/null
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    connection = Connection(Config.default())
    ctx = ClientContext.from_header(encoded, connection)

    assert ctx.org.id == "00DJS0000000123ABC"
    assert ctx.org.user.username == "user@example.tld"
    assert ctx.request_id == "req-456"
    assert ctx.access_token == "access-token-xyz"
    assert ctx.api_version == "v57.0"
    assert ctx.namespace is None
