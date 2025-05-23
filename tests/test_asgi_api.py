import pytest
import json
import base64

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from heroku_applink.middleware import IntegrationAsgiMiddleware

app = FastAPI()
app.add_middleware(IntegrationAsgiMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/client-context")
async def client_context(request: Request):
    data_api = request.scope["client-context"].data_api

    return {"data_api_populated": data_api is not None}



@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_raises_client_context_error(client):
    with pytest.raises(ValueError, match="x-client-context not set"):
        client.get("/")

def test_scoped_client_context(client):
    client_context = {
        "orgId": "00DJS0000000123ABC",
        "orgDomainUrl": "https://example-domain-url.my.salesforce.com",
        "userContext": {
            "userId": "005JS000000H123",
            "username": "user@example.tld"
        },
        "requestId": "006JS000000H123ABC",
        "accessToken": "006JS000000H123ABC",
        "apiVersion": "50.0",
        "namespace": "heroku_applink",
    }

    response = client.get(
        "/client-context",
        headers={
            "x-client-context": base64.b64encode(json.dumps(client_context).encode()).decode()
        }
    )

    assert response.status_code == 200
    assert response.json() == {"data_api_populated": True}
