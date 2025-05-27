# heroku_applink/exceptions.py

import aiohttp

class ClientError(Exception):
    """Raised when there is an error with the HTTP client."""
    pass

class UnexpectedRestApiResponsePayload(Exception):
    """Raised when the API response is not in the expected format."""
    pass
