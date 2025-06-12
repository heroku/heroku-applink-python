# Python SDK for Heroku AppLink

This library provides basic functionality for building Python apps that use
Heroku AppLink to secure communication and credential sharing with a Salesforce
org.

Though the interaction with AppLink is simple and easy to hand code, using the
SDK will quickstart your project experience.

Use of this project with Salesforce is subject to the [TERMS_OF_USE.md](TERMS_OF_USE.md) document.

[Documentation](docs/heroku_applink/index.md) for the SDK is available and is generated
from the source code.

## Generate Documentation

Install the doc dependency group.

```shell
$ uv sync --group docs
```

Generate the documentation.

```shell
$ uv run pdoc3 --template-dir templates/python heroku_applink -o docs --force
```

## Development

### Setting Up the Development Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/heroku/heroku-applink-python.git
    cd heroku-applink-python
    ```

2. Install Dependencies:

    Install the `uv` package manager:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    Sync all dependencies:

    ```bash
    uv sync --all-extras
    ```

3. Sync Development Dependencies:

    ```bash
    uv sync --all-extras --dev
    ```

### Running Tests

1. Run the full test suite:

    ```bash
    # Run all tests
    uv run pytest

    # Run all tests with coverage
    uv run pytest --cov=heroku_applink.data_api --cov-report=term-missing -v
    ```

2. Run a single test:

    ```bash
    # Run a specific test file
    uv run pytest <path_to_test_file>/test_specific_file.py

    # Run a specific test file with coverage
    uv run pytest tests/data_api/test_data_api_record.py::test_some_specific_case \
        --cov=heroku_applink.data_api
    ```

3. Run tests with a specific Python version:

    ```bash
    pyenv shell 3.12.2  # Or any installed version
    uv venv
    source .venv/bin/activate
    uv sync --all-extras --dev
    uv run pytest
    ```

4. Run tests across multiple Python versions with Tox:

    ```bash
    uv sync --all-extras --dev
    uv run tox
    ```

### Linting and Code Quality

1. Run the Ruff linter:

    ```bash
    # Check the code for issues
    uv run ruff check .

    # Automatically fix issues
    uv run ruff check . --fix

    # Check a specific directory (e.g., heroku_applink)
    uv run ruff check heroku_applink/

    # Format the codebase
    uv run ruff format .
    ```

## Usage Examples

For more detailed information about the SDK's capabilities, please refer to the [full documentation](docs/heroku_applink/index.md).

### Basic Setup

Install the package.

```shell
$ uv pip install heroku_applink
```

#### ASGI

If you are using an ASGI framework (like FastAPI), you can use the `IntegrationAsgiMiddleware` to automatically populate the `client-context` in the request scope.

```python
# FastAPI example
import asyncio
import heroku_applink as sdk
from fastapi import FastAPI

config = sdk.Config(request_timeout=5)

app = FastAPI()
app.add_middleware(sdk.IntegrationAsgiMiddleware, config=config)

@app.get("/")
def get_root():
    return {"root": "page"}


@app.get("/accounts")
def get_accounts():
    data_api = sdk.get_client_context().data_api
    result = asyncio.run(query_accounts(data_api))
    
    accounts = [
        {
            "id": record.fields["Id"],
            "name": record.fields["Name"]
        }
        for record in result.records
    ]
    return accounts

async def query_accounts(data_api):
    query = "SELECT Id, Name FROM Account"
    result = await data_api.query(query)
    for record in result.records:
        print("===== account record", record)
    return result
```

#### WSGI

If you are using a WSGI framework (like Flask), you can use the `IntegrationWsgiMiddleware` to automatically populate the `client-context` in the request environment.

```python
from flask import Flask, jsonify, request

import heroku_applink as sdk

config = sdk.Config(request_timeout=5)
app = Flask(__name__)
app.wsgi_app = sdk.IntegrationWsgiMiddleware(app.wsgi_app, config=config)


@app.route("/")
def index():
    return jsonify({"message": "Hello, World!"})


@app.route("/accounts")
def get_accounts():
    data_api = sdk.get_client_context().data_api
    query = "SELECT Id, Name FROM Account"
    result = data_api.query(query)

    return jsonify({"accounts": [record.get("Name") for record in result.records]})
```

#### Directly from the x-client-context header

If you are not using a framework, you can manually extract the `x-client-context`
header and use the `DataAPI` class to query the Salesforce org.

```python
from heroku_applink.data_api import DataAPI

header = request.headers.get("x-client-context")
decoded = base64.b64decode(header)
data = json.loads(decoded)

data_api = DataAPI(
    org_domain_url=data["orgDomainUrl"],
    api_version=data["apiVersion"],
    access_token=data["accessToken"],
)

result = data_api.query("SELECT Id, Name FROM Account")
```

#### Directly using the get_authorization function

```python
import asyncio
import heroku_applink as sdk


async def main():
    # Get authorization for a developer
    authorization = await sdk.get_authorization(
        developer_name="your_developer_name",
        attachment_or_url="HEROKU_APPLINK"
    )

    # Access the context properties
    print(f"Organization ID: {authorization.org.id}")
    print(f"User ID: {authorization.org.user.id}")
    print(f"Username: {authorization.org.user.username}")

    # Use the DataAPI to make queries
    query = "SELECT Id, Name FROM Account"
    result = await authorization.data_api.query(query)
    for record in result.records:
        print(f"Account: {record}")

# Run the async function
asyncio.run(main())
```
