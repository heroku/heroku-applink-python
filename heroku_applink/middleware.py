import contextvars
from .context import ClientContext
import json

client_context: contextvars.ContextVar = contextvars.ContextVar("client_context")

def from_request(request) -> ClientContext:
    header = request.headers.get("x-client-context")

    if not header:
        raise ValueError("x-client-context not set")

    return ClientContext.from_http(header)


class IntegrationWsgiMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        ctx = from_request(request)
        client_context.set(ctx)

        response = self.get_response(request)
        return response

class IntegrationAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            headers = dict(scope["headers"])
            header = headers.get(b"x-client-context")
            if not header:
                raise ValueError("x-client-context not set")

            ctx = ClientContext.from_header(header)
            client_context.set(ctx)
            scope["client-context"] = ctx

            await self.app(scope, receive, send)
        except Exception as e:
            raise e

    async def _send_error_response(self, send, status_code: int, detail: str):
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps({"detail": detail}).encode(),
        })
