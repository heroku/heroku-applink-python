import aiohttp

from .config import Config

class Session:
    def __init__(self, config: Config):
        self.session = aiohttp.ClientSession(
            # Disable cookie storage using `DummyCookieJar`, given that we
            # don't need cookie support.
            cookie_jar=aiohttp.DummyCookieJar(),
            timeout=aiohttp.ClientTimeout(
                total=config.request_timeout,
                connect=config.connect_timeout,
                sock_connect=config.socket_connect,
                sock_read=config.socket_read,
            ),
        )

    def client(self) -> aiohttp.ClientSession:
        return self.session
