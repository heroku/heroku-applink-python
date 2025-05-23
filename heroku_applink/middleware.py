import contextvars
from .context import ClientContext

client_context: contextvars.ContextVar = contextvars.ContextVar("client_context")

def from_request(request) -> ClientContext:
    header = request.headers.get("x-client-context")

    if not header:
        raise ValueError("x-client-context not set")

    return ClientContext.from_http(header)


class IntegrationWsgiMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        header = environ.get("HTTP_X_CLIENT_CONTEXT")

        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header)
        client_context.set(ctx)

        return self.app(environ, start_response)

class IntegrationAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        header = headers.get(b"x-client-context")
        if not header:
            raise ValueError("x-client-context not set")

        ctx = ClientContext.from_header(header)
        client_context.set(ctx)
        scope["client-context"] = ctx

        await self.app(scope, receive, send)
