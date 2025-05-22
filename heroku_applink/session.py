import aiohttp

from .config import Config

class Session:
    """
    A session for making asynchronous HTTP requests.
    """

    def __init__(self, config: Config):
        self._config = config
        self._session = None

    def request(self, method, url, headers=None, data=None):
        """
        Make an HTTP request to the given URL.
        """
        return self._client().request(method, url, headers=headers, data=data)

    async def close(self):
        """
        Close the session.
        """
        if self._session:
            self._session.close()

    def _client(self) -> aiohttp.ClientSession:
        """
        Lazily get the underlying `aiohttp.ClientSession`. This session is
        persisted so we can take advantage of connection pooling.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession(
                # Disable cookie storage using `DummyCookieJar`, given that we
                # don't need cookie support.
                cookie_jar=aiohttp.DummyCookieJar(),
                timeout=aiohttp.ClientTimeout(
                    total=self._config.request_timeout,
                    connect=self._config.connect_timeout,
                    sock_connect=self._config.socket_connect,
                    sock_read=self._config.socket_read,
                ),
            )
        return self._session
