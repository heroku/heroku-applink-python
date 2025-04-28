import base64
import json
import pytest
from heroku_applink.context import User, Org, ClientContext

def test_user_initialization():
    user = User(
        id="005JS000000H123",
        username="user@example.tld"
    )
    assert user.id == "005JS000000H123"
    assert user.username == "user@example.tld"

def test_org_initialization():
    user = User(
        id="005JS000000H123",
        username="user@example.tld"
    )
    org = Org(
        id="00DJS0000000123ABC",
        domain_url="https://example-domain-url.my.salesforce.com",
        user=user
    )
    assert org.id == "00DJS0000000123ABC"
    assert org.domain_url == "https://example-domain-url.my.salesforce.com"
    assert org.user == user

def test_client_context_initialization():
    user = User(
        id="005JS000000H123",
        username="user@example.tld"
    )
    org = Org(
        id="00DJS0000000123ABC",
        domain_url="https://example-domain-url.my.salesforce.com",
        user=user
    )
    context = ClientContext(
        org=org,
        request_id="test-request-id",
        access_token="test-access-token",
        api_version="v1",
        namespace="test-namespace",
        data_api=None  # We'll test this separately
    )
    assert context.org == org
    assert context.request_id == "test-request-id"
    assert context.access_token == "test-access-token"
    assert context.api_version == "v1"
    assert context.namespace == "test-namespace"

def test_client_context_from_header():
    # Create test data
    test_data = {
        "orgId": "00DJS0000000123ABC",
        "orgDomainUrl": "https://example-domain-url.my.salesforce.com",
        "userContext": {
            "userId": "005JS000000H123",
            "username": "user@example.tld"
        },
        "requestId": "test-request-id",
        "accessToken": "test-access-token",
        "apiVersion": "v1",
        "namespace": "test-namespace"
    }
    
    # Encode the test data
    encoded_data = base64.b64encode(json.dumps(test_data).encode()).decode()
    
    # Create context from header
    context = ClientContext.from_header(encoded_data)
    
    # Verify org data
    assert context.org.id == test_data["orgId"]
    assert context.org.domain_url == test_data["orgDomainUrl"]
    assert context.org.user.id == test_data["userContext"]["userId"]
    assert context.org.user.username == test_data["userContext"]["username"]
    
    # Verify other context data
    assert context.request_id == test_data["requestId"]
    assert context.access_token == test_data["accessToken"]
    assert context.api_version == test_data["apiVersion"]
    assert context.namespace == test_data["namespace"]
    
    # Verify DataAPI was initialized correctly
    assert context.data_api is not None
    assert context.data_api.org_domain_url == test_data["orgDomainUrl"]
    assert context.data_api.api_version == test_data["apiVersion"]
    assert context.data_api.access_token == test_data["accessToken"]

def test_client_context_from_header_invalid_base64():
    with pytest.raises(Exception):
        ClientContext.from_header("invalid-base64")

def test_client_context_from_header_invalid_json():
    invalid_json = base64.b64encode(b"invalid-json").decode()
    with pytest.raises(Exception):
        ClientContext.from_header(invalid_json)

def test_client_context_from_header_missing_fields():
    test_data = {
        "orgId": "00DJS0000000123ABC",
        # Missing required fields
    }
    encoded_data = base64.b64encode(json.dumps(test_data).encode()).decode()
    with pytest.raises(Exception):
        ClientContext.from_header(encoded_data) 