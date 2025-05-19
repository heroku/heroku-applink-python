# Heroku Applink Python Package FAQ

## General Questions

### What is Heroku Applink?
Heroku Applink is a Python package that provides integration between Heroku applications and Salesforce. It enables secure communication and data exchange between Heroku apps and Salesforce orgs.

### What are the system requirements?
- Python 3.8 or higher
- A Heroku account
- A Salesforce org
- Required environment variables for authentication

## Installation and Setup

### How do I install the package?
```bash
pip install heroku-applink
```

### What environment variables do I need to set up?
Required environment variables:
- `HEROKU_APPLINK_API_URL`: Your Heroku Applink endpoint URL
- `HEROKU_APPLINK_TOKEN`: Your authentication token

Optional environment variables:
- `HEROKU_APPLINK_STAGING_API_URL`: Staging endpoint URL (if using staging environment)
- Custom attachment variables (if using multiple attachments):
  - `{ATTACHMENT_NAME}_API_URL`
  - `{ATTACHMENT_NAME}_TOKEN`

## Usage

### How do I get started with basic authorization?
```python
from heroku_applink.addons.heroku_applink import get_authorization

async def my_function():
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

### How do I handle errors?
The package provides several exception types:
- `ValueError`: For invalid input parameters
- `EnvironmentError`: For missing environment variables
- `RuntimeError`: For API request failures

Example error handling:
```python
try:
    client_context = await get_authorization("developer_name")
except ValueError as e:
    print(f"Invalid input: {e}")
except EnvironmentError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

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

### How do I set up test environment variables?
Create a `.env.test` file:
```env
HEROKU_APPLINK_API_URL=https://your-test-endpoint.com
HEROKU_APPLINK_TOKEN=your-test-token
```

## Troubleshooting

### Common Issues and Solutions

#### Authorization Failures
**Problem**: Getting "Authorization request failed" error
**Solutions**:
1. Verify your environment variables are set correctly
2. Check if your token is valid and not expired
3. Ensure your API URL is correct and accessible

#### Environment Variable Issues
**Problem**: "Missing environment variables" error
**Solutions**:
1. Check if all required variables are set
2. Verify variable names match exactly
3. Ensure variables are in the correct environment

#### Connection Timeouts
**Problem**: Connection timeout errors
**Solutions**:
1. Check your network connection
2. Verify the API endpoint is accessible
3. Check if your firewall is blocking the connection

## Best Practices

### Security
1. Never commit environment variables to version control
2. Use different tokens for development and production
3. Regularly rotate your authentication tokens

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