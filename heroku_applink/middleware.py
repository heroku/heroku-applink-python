from contextvars import ContextVar

from .config import Config
from .context import ClientContext
from .connection import Connection

client_context: ContextVar[ClientContext] = ContextVar("client_context")

class IntegrationWsgiMiddleware:
    def __init__(self, app, config=Config.default()):
        self.app = app
        self.config = config
        self.connection = Connection(self.config)

    def __call__(self, environ, start_response):
        header = environ.get("HTTP_X_CLIENT_CONTEXT")

        if not header:
            raise ValueError("x-client-context not set")

        client_context.set(ClientContext.from_header(header, self.connection))

        return self.app(environ, start_response)

class IntegrationAsgiMiddleware:
    def __init__(self, app, config=Config.default()):
        self.app = app
        self.config = config
        self.connection = Connection(self.config)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        header = headers.get(b"x-client-context")
        if not header:
            raise ValueError("x-client-context not set")

        client_context.set(ClientContext.from_header(header, self.connection))

        await self.app(scope, receive, send)
