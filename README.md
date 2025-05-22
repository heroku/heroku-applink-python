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

### Basic Setup

1. Install the package:
    ```bash
    uv pip install heroku_applink
    ```

2. Using the get_authorization function:
    ```python
    import asyncio
    from heroku_applink.addons.heroku_applink import get_authorization

    async def main():
        # Get authorization for a developer
        # You can provide either a developer name or an attachment/URL
        context = await get_authorization(
            developer_name="your_developer_name",
            attachment_or_url="HEROKU_APPLINK"  # Optional: defaults to HEROKU_APPLINK if not provided
        )
        
        # Access the context properties
        print(f"Organization ID: {context.org.id}")
        print(f"User ID: {context.org.user.id}")
        print(f"Username: {context.org.user.username}")
        
        # Use the DataAPI to make queries
        query = "SELECT Id, Name FROM Account"
        result = await context.data_api.query(query)
        for record in result.records:
            print(f"Account: {record}")

    # Run the async function
    asyncio.run(main())
    ```

3. Add the middleware to your web framework:

    ```python
    # FastAPI example
    import asyncio
    import heroku_applink as sdk
    from fastapi import FastAPI

    app = FastAPI()
    app.add_middleware(sdk.IntegrationAsgiMiddleware)


    @app.get("/")
    def get_root():
        return {"root": "page"}


    @app.get("/accounts")
    def get_accounts():
        dataapi = sdk.context.get()
        asyncio.run(query_accounts(dataapi))
        return {"Some": "Accounts"}


    async def query_accounts(dataapi):
        query = "SELECT Id, Name FROM Account"
        result = await dataapi.query(query)
        for record in result.records:
            print("===== account record", record)
    ```

For more detailed information about the SDK's capabilities, please refer to the [full documentation](docs/heroku_applink/index.md).
