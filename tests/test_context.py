import base64
import json
import pytest
from heroku_applink.models import User, Org, OrgType
from heroku_applink.context import ClientContext

class FakeDataAPI:
    """Fake DataAPI class for testing without real dependencies."""
    def __init__(self, org_domain_url, api_version, access_token):
        self.org_domain_url = org_domain_url
        self.api_version = api_version
        self.access_token = access_token

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
    org = Org(id="00DJS0000000123ABC", domain_url="https://example-domain.my.salesforce.com", user=user, type=OrgType.SALESFORCE)
    assert org.id == "00DJS0000000123ABC"
    assert org.domain_url.startswith("https://")
    assert isinstance(org.user, User)

def test_client_context_creation():
    user = User(id="005JS000000H123", username="user@example.tld")
    org = Org(id="00DJS0000000123ABC", domain_url="https://example-domain.my.salesforce.com", user=user, type=OrgType.SALESFORCE)
    ctx = ClientContext(
        org=org,
        data_api=FakeDataAPI(
            org_domain_url=org.domain_url,
            api_version="v57.0",
            access_token="fake_token",
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

    ctx = ClientContext.from_header(encoded)

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
