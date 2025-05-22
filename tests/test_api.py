import pytest
import time

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from heroku_applink.middleware import IntegrationAsgiMiddleware


app = FastAPI()
app.add_middleware(IntegrationAsgiMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# Test client fixture
@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_raises_client_context_error(client):
    with pytest.raises(ValueError, match="x-client-context not set"):
        client.get("/")

# def test_endpoint_returns_hello_world(client):
#     response = client.get("/")
#     assert response.status_code == 200
#    assert response.json() == {"message": "Hello, World!"}
