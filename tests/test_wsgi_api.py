import pytest

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
    return jsonify({"data_api_populated": request.scope["client-context"] is not None})

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_endpoint_raises_client_context_error(client):
    with pytest.raises(ValueError, match="x-client-context not set"):
        client.get("/")

def test_scoped_client_context(client):
    response = client.get("/client-context", headers={"x-client-context": "test"})
    assert response.status_code == 200
    assert response.json() == {"data_api_populated": True}
