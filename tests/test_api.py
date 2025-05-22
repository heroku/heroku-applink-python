import pytest
import time
import json
import base64

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

import heroku_applink as sdk
from heroku_applink.middleware import IntegrationAsgiMiddleware


app = FastAPI()
app.add_middleware(IntegrationAsgiMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/client-context")
async def client_context(request: Request):
    data_api = request.scope["client-context"].data_api
    result = await data_api.query("SELECT Id, Name FROM Account")
    return {"message": "Hello, World!", "result": result}



@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_raises_client_context_error(client):
    with pytest.raises(ValueError, match="x-client-context not set"):
        client.get("/")

def test_scoped_client_context(client):
    context = {
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
            "x-client-context": base64.b64encode(json.dumps(context).encode()).decode()
        }
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}



