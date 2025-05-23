import pytest
import json
import base64

from flask import Flask, jsonify, request
from flask.testing import FlaskClient

from heroku_applink.middleware import IntegrationWsgiMiddleware

app = Flask(__name__)
app.wsgi_app = IntegrationWsgiMiddleware(app.wsgi_app)

@app.route("/")
def index():
    return jsonify({"message": "Hello, World!"})

@app.route("/client-context")
def client_context():
    data_api = request.environ['client-context'].data_api

    return jsonify({"data_api_populated": data_api is not None})

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def client_context():
    return {
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

def test_endpoint_raises_client_context_error(client):
    with pytest.raises(ValueError, match="x-client-context not set"):
        client.get("/")

def test_scoped_client_context(client, client_context):
    response = client.get(
        "/client-context",
        headers={
            "x-client-context": base64.b64encode(json.dumps(client_context).encode()).decode()
        }
    )

    assert response.status_code == 200
    assert response.json == {"data_api_populated": True}
