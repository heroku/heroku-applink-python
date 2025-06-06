# Heroku Applink Python Package FAQ

## General Questions

### What is Heroku Applink Python SDK?
Heroku Applink Python SDK is a Python package that provides integration between Heroku applications and Salesforce. It enables secure communication and data exchange between Heroku apps and Salesforce orgs.

### What are the system requirements?
- Python 3.10 or higher
- A Heroku account
- A Salesforce org
- Required environment variables for authentication

## Installation and Setup

### How do I install the package?

Using pip:
```bash
pip install heroku-applink
```

Using uv:
```bash
uv pip install heroku-applink
```

Using requirements.txt:
```txt
heroku-applink>=0.1.0
aiohttp>=3.11.12
orjson>=3.10.15
```

To add it to your project's dependencies in pyproject.toml:
```toml
[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
requires-python = ">=3.10"
dependencies = [
    "heroku-applink>=0.1.0",
    "aiohttp>=3.11.12",
    "orjson>=3.10.15"
]

[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "ruff>=0.1.0",
    "coverage>=7.0.0"
]
```

### What environment variables do I need to set up?
Required environment variables:
- `HEROKU_APPLINK_API_URL`: Your Heroku Applink endpoint URL
- `HEROKU_APPLINK_TOKEN`: Your authentication token
- `HEROKU_APP_ID`: The UUID of your Heroku app - see [Heroku Labs: Dyno Metadata](https://devcenter.heroku.com/articles/dyno-metadata)

Optional environment variables:
- `HEROKU_APPLINK_STAGING_API_URL`: Staging endpoint URL (if using staging environment)
- Custom attachment variables (if using multiple attachments):
  - `{ATTACHMENT_NAME}_API_URL`
  - `{ATTACHMENT_NAME}_TOKEN`

For color/alias support (e.g., "PURPLE"):
```bash
export HEROKU_APPLINK_PURPLE_API_URL=https://api.heroku-applink.com
export HEROKU_APPLINK_PURPLE_TOKEN=<your-addon-token>
```

**Best Practices for Environment Variables:**
1. Never commit environment variables to version control
2. Use different tokens for development and production
3. Regularly rotate your authentication tokens
4. For testing, create a `.env.test` file with test credentials

## Usage

### How do I get started with basic authorization?
```python
from heroku_applink.addons.heroku_applink import get_authorization

async def my_function():
    # You must provide a valid developer name (org alias)
    client_context = await get_authorization("your_developer_name")
    # Use client_context to interact with Salesforce
```

### How do I use custom attachments?
```python
# Using a custom attachment
client_context = await get_authorization(
    "your_developer_name",
    attachment_name_or_url="CUSTOM_ATTACHMENT"
)
```

### How do I handle errors and timeouts?
The package provides several exception types:
- `ValueError`: For invalid input parameters
- `EnvironmentError`: For missing environment variables
- `RuntimeError`: For API request failures
- `ClientError`: Network issues (timeouts, DNS, etc.)
- `UnexpectedRestApiResponsePayload`: Non-JSON or malformed JSON from Salesforce

Example error handling:
```python
from heroku_applink.exceptions import ClientError, UnexpectedRestApiResponsePayload

try:
    client_context = await get_authorization("developer_name")
except ValueError as e:
    print(f"Invalid input: {e}")
except EnvironmentError as e:
    print(f"Configuration error: {e}")
except ClientError as e:
    print(f"Network error: {e}")
except UnexpectedRestApiResponsePayload as e:
    print(f"Invalid response: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

### How do I integrate the SDK into my application?
Use the provided middleware to populate a ContextVar with your ClientContext:

#### WSGI (e.g. Django)
```python
# settings.py
MIDDLEWARE = [
    "heroku_applink.middleware.IntegrationWsgiMiddleware",
    # ... your other middleware ...
]
```

#### ASGI (e.g. FastAPI)
```python
# main.py
from heroku_applink.middleware import IntegrationAsgiMiddleware

app = IntegrationAsgiMiddleware(app)
```

Then in your handlers, retrieve context via:
```python
from heroku_applink.middleware import client_context
ctx = client_context.get()
```

For custom frameworks, you can manually parse the header:
```python
from heroku_applink.context import ClientContext
ctx = ClientContext.from_header(request.headers["x-client-context"])
```

### How can I perform CRUD operations against Salesforce?
```python
# Query
result = await ctx.data_api.query("SELECT Id, Name FROM Account")
for record in result.records:
    print(record.fields["Id"], record.fields["Name"])

# Create
new_id = await ctx.data_api.create(
    Record(type="Account", fields={"Name": "Acme Co"})
)

# Update
await ctx.data_api.update(
    Record(type="Account", fields={"Id": new_id, "Phone": "123-4567"})
)

# Delete
await ctx.data_api.delete("Account", new_id)
```

### How do I run multiple operations atomically?
Use the UnitOfWork composite API:
```python
from heroku_applink.data_api.unit_of_work import UnitOfWork
from heroku_applink.data_api.record import Record

uow = UnitOfWork()
ref_acc = uow.register_create(Record(type="Account", fields={"Name":"X"}))
uow.register_create(Record(type="Contact", fields={
    "FirstName":"Joe", 
    "LastName":"Smith", 
    "AccountId": ref_acc
}))
results = await ctx.data_api.commit_unit_of_work(uow)
# results[ref_acc] gives the new Account ID
```

### Why are my record fields case-sensitive?
Unlike the Node.js SDK, the Python SDK stores `Record.fields` in a plain dict. Ensure you use the exact Salesforce field name casing (e.g. "Id", not "id"). To add case-insensitive lookup, wrap or subclass your dict to normalize keys to lower-case.

## Testing

### How do I run the tests?
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/addons/test_addons.py

# Run functional tests
pytest -m functional
```

## **Common Issues and Solutions:**

### 1. Missing or Incorrect Environment Variables
**Symptom**: `EnvironmentError` raised during `Authorization.find(...)`.

**Root Cause**:
- Missing required env vars like `HEROKU_APPLINK_<COLOR>_API_URL` and `_TOKEN`, or custom attachment names.

**Fix**:
- Double-check the presence of:
  - `HEROKU_APPLINK_<COLOR>_API_URL`
  - `HEROKU_APPLINK_<COLOR>_TOKEN`
  - Or `<ATTACHMENT>_API_URL` / `_TOKEN`

---

### 2. Invalid `attachment_or_url` Argument
**Symptom**: Unexpected token resolution failure or URL not found error.

**Fix**:
- Use valid attachment names or full URLs.
- Ensure URLs exactly match env values (case-insensitive, including trailing slashes).

---

### 3. Forgetting to `await` the `Connection.request(...)` Call
**Symptom**: Warning: coroutine was never awaited.

**Fix**:
- Always `await` the result of `request()`:
  ```python
  response = await connection.request(...)
  ```

---

### 4. Unclosed `aiohttp.ClientSession`
**Symptom**: Resource warnings / connection pool errors.

**Fix**:
- Call `await connection.close()` explicitly when you're done (or trust middleware to manage it).
- Ensure sessions are not garbage collected in unexpected ways.

---

### 5. Missing `x-client-context` Header
**Symptom**: `ValueError: x-client-context not set`

**Cause**:
- Middleware (`IntegrationAsgiMiddleware` or `IntegrationWsgiMiddleware`) not installed or header missing.

**Fix**:
- Ensure you're using the appropriate middleware for your framework:
  ```python
  app.add_middleware(sdk.IntegrationAsgiMiddleware, config=sdk.Config(...))
  ```

---

### 6. Using `get_client_context()` Outside a Middleware Context
**Symptom**: `ValueError: No client context found`

**Fix**:
- Call `get_client_context()` only during a request routed through the middleware.

---

### 7. Missing `"Id"` Field on `update()` Operations
**Symptom**: `MissingFieldError`

**Fix**:
- Make sure the `Record` passed to `.update(...)` contains a valid `"Id"`:
  ```python
  Record(type="Account", fields={"Id": "...", "Name": "Updated"})
  ```

---

### 8. Incorrect Field Nesting or Binary Data Format
**Symptom**: Salesforce API errors / decoding errors.

**Fix**:
- Ensure binary fields (e.g., `VersionData` in `ContentVersion`) are passed as `bytes` — the SDK base64 encodes them.
- Nested records and subqueries are automatically parsed, but manual construction must respect Salesforce’s expected structure.

---

### 9. Reusing or Mutating `ReferenceId` Objects
**Symptom**: Unexpected overwrite or graph resolution errors.

**Fix**:
- Treat `ReferenceId` as immutable. Let `UnitOfWork` generate and manage them.

---

### 10. Missing `await` on `commit_unit_of_work(...)`
**Symptom**: Unit of work never runs or throws coroutine warnings.

**Fix**:
- Always `await`:
  ```python
  result = await data_api.commit_unit_of_work(uow)
  ```

---
## Best Practices

### Performance
1. Reuse ClientContext when possible
2. Use appropriate timeouts for your use case
3. Handle connection pooling appropriately

### Error Handling
1. Always implement proper error handling
2. Log errors for debugging
3. Implement retry logic for transient failures

## Support

### Where can I get help?
- GitHub Issues: [Report bugs or request features](https://github.com/heroku/heroku-applink-python/issues)
- Documentation: [Read the full documentation](https://github.com/heroku/heroku-applink-python/docs)
- Stack Overflow: Use the tag `heroku-applink`

### How do I report a bug?
1. Check if the issue is already reported
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Relevant logs or error messages

## Contributing

### How can I contribute?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Submit a pull request

### What are the contribution guidelines?
1. Follow PEP 8 style guide
2. Write clear commit messages
3. Add tests for new features
4. Update documentation
5. Ensure all tests pass

## Version History

### How do I check the current version?

Using pip:
```bash
pip show heroku-applink
```

Using uv:
```bash
uv pip show heroku-applink
```

You can also check the version programmatically:
```python
import heroku_applink
print(heroku_applink.__version__)
```

### How do I upgrade?
```bash
pip install --upgrade heroku-applink
```

## Additional Resources

### Documentation
- [API Reference](https://github.com/heroku/heroku-applink-python/docs/api.md)
- [Examples](https://github.com/heroku/heroku-applink-python/docs/examples.md)
- [Changelog](https://github.com/heroku/heroku-applink-python/CHANGELOG.md)

### Related Projects
- [Heroku Platform API](https://devcenter.heroku.com/articles/platform-api-reference)
- [Salesforce REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)

### How do I generate up-to-date docs?
Install and run pdoc3:

```bash
pip install pdoc3
pdoc --html --output-dir docs --force heroku_applink
```
