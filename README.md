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
