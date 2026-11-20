# Heroku AppLink SDK for Python

The Heroku AppLink SDK lets Heroku apps find out who invoked them from Salesforce, and look up the credentials of stored [Heroku AppLink](https://devcenter.heroku.com/articles/heroku-applink) authorizations. Apps call Salesforce APIs with the Salesforce client of their choice, using the org and credentials the SDK returns.

## Installation

```sh
pip install heroku-applink
```

Requires Python 3.12 or newer.

## Handling invocations from Salesforce

When Salesforce invokes your app through AppLink, `parse_invocation_context` decodes the `x-client-context` header of the request:

```python
from flask import Flask, request

from heroku_applink import InvalidInboundDataError, parse_invocation_context

app = Flask(__name__)


@app.post("/accounts")
def accounts():
    try:
        context = parse_invocation_context(request.headers.get)
    except InvalidInboundDataError:
        return "Not an AppLink request", 400

    print(f"Invoked by {context.user.username} in org {context.org.id}")
    return {"requestId": context.request_id}
```

`context.credentials` holds an access token for the invoking user if the invocation carries one.

## Looking up an authorization

`get_authorization` looks up a stored authorization through the AppLink API. Pass the org and credentials to a Salesforce client, for example [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce):

```python
from simple_salesforce import Salesforce

from heroku_applink import get_authorization

context = get_authorization("<my-authorization>")

salesforce = Salesforce(
    instance_url=context.org.domain_url,
    session_id=context.credentials.access_token,
    version=context.org.api_version,
)

result = salesforce.query("SELECT Id, Name FROM Account")
```

To use another AppLink add-on attachment than the default `HEROKU_APPLINK`, pass its name, color, or API URL:

```python
# By name, reads HEROKU_APPLINK_PURPLE_API_URL and HEROKU_APPLINK_PURPLE_TOKEN
context = get_authorization("<my-authorization>", attachment="HEROKU_APPLINK_PURPLE")

# By color, reads the same config vars as the name
context = get_authorization("<my-authorization>", attachment="purple")

# By API URL, uses the attachment whose _API_URL config var holds that URL
api_url = os.environ["HEROKU_APPLINK_PURPLE_API_URL"]
context = get_authorization("<my-authorization>", attachment=api_url)
```

An API URL must match the value of exactly one of the app's config vars ending in `_API_URL`.

Every lookup sends a request to the AppLink API. You can keep a context and reuse it until `context.credentials.expiration`, then look it up again for a new access token.

### Async apps

`get_authorization` is blocking. It makes a network request and, if the request fails, retries it, which can take up to about 22 seconds in total. In an async app, such as one built with FastAPI or Starlette, run it in a worker thread so it doesn't block the event loop:

```python
import asyncio

context = await asyncio.to_thread(get_authorization, "<my-authorization>")
```

## Errors

All errors are subclasses of `AppLinkError`:

| Error                        | Cause                                                             |
| ---------------------------- | ----------------------------------------------------------------- |
| `InvalidInboundDataError`    | The `x-client-context` header is missing or malformed.            |
| `ConfigurationError`         | The input or the AppLink config vars are missing or invalid.      |
| `TransportError`             | The request to the AppLink API didn't complete.                   |
| `HTTPError`                  | The AppLink API responded with a non-2xx `status`, such as `404`. |
| `UnusableAuthorizationError` | The authorization's `status` isn't `authorized`.                  |
| `UnexpectedResponseError`    | The AppLink API response doesn't have the expected content.       |

## Development

```sh
uv run pytest
uv run ruff check
uv run ruff format
uv run mypy src tests
```

The tests read the shared [test vectors](https://github.com/heroku/heroku-applink-sdks) from the `test-vectors` submodule. Run `git submodule update --init` after cloning to fetch them.
