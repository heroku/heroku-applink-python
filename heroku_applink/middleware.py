import aiohttp
import contextvars

from .config import Config
from .context import ClientContext

client_context: contextvars.ContextVar = contextvars.ContextVar("client_context")

class BaseIntegrationMiddleware:
    def _build_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            cookie_jar=aiohttp.DummyCookieJar(),
            timeout=aiohttp.ClientTimeout(
                total=self.config.request_timeout,
                connect=self.config.connect_timeout,
                sock_connect=self.config.socket_connect,
                sock_read=self.config.socket_read,
            ),
        )

class IntegrationWsgiMiddleware(BaseIntegrationMiddleware):
    def __init__(self, get_response, config: Config) -> None:
        self.get_response = get_response
        self.config = config
        self.session = self._build_session()

    def __call__(self, request):
        header = request.headers.get("x-client-context")

        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header, self.session)
        client_context.set(ctx)

        response = self.get_response(request)
        return response

class IntegrationAsgiMiddleware(BaseIntegrationMiddleware):
    def __init__(self, app, config: Config):
        self.app = app
        self.config = config
        self.session = self._build_session()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        header = headers.get(b"x-client-context")
        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header, self.session)
        client_context.set(ctx)
        scope["client-context"] = ctx

        await self.app(scope, receive, send)
