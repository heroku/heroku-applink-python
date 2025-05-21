import contextvars

from .config import Config
from .context import ClientContext

client_context: contextvars.ContextVar = contextvars.ContextVar("client_context")

class IntegrationWsgiMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        header = request.headers.get("x-client-context")

        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header, self.config)
        client_context.set(ctx)

        response = self.get_response(request)
        return response

class IntegrationAsgiMiddleware:
    def __init__(self, app, config: Config):
        self.app = app
        self.config = config

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        header = headers.get(b"x-client-context")
        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header, self.config)
        client_context.set(ctx)
        scope["client-context"] = ctx

        await self.app(scope, receive, send)
