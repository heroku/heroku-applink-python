import aiohttp

from .config import Config

class Session:
    def __init__(self, config: Config):
        self._config = config
        self._session = None

    def client(self) -> aiohttp.ClientSession:
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

    def request(self, method, url, headers=None, data=None):
        return self.client().request(method, url, headers=headers, data=data)

    async def close(self):
        if self._session:
            self._session.close()
