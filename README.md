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
    uv sync --all-extras --dev
    ```

3. Install Development Dependencies:

    ```bash
    pip install -e ".[dev]"
    ```

### Running Tests

1. Run the full test suite:

    ```bash
    # Run all tests
    pytest

    # Run all tests with coverage
    pytest --cov=heroku_applink.data_api --cov-report=term-missing -v
    ```

2. Run a single test:

    ```bash
    # Run a specific test file
    pytest <path_to_test_file>/test_specific_file.py

    # Run a specific test file with coverage
    pytest tests/data_api/test_data_api_record.py::test_some_specific_case \
        --cov=heroku_applink.data_api
    ```

3. Run tests with a specific Python version:

    ```bash
    pyenv shell 3.12.2  # Or any installed version
    uv venv
    source .venv/bin/activate
    uv sync --all-extras --dev
    pytest
    ```

4. Run tests across multiple Python versions with Tox:

    ```bash
    pip install tox tox-uv
    tox
    ```

### Linting and Code Quality

1. Run the Ruff linter:

    ```bash
    # Check the code for issues
    ruff check .

    # Automatically fix issues
    ruff check . --fix

    # Check a specific directory (e.g., heroku_applink)
    ruff check heroku_applink/

    # Format the codebase
    ruff format .
    ```
