"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import uuid

from .config import Config
from .context import ClientContext, set_client_context
from .connection import Connection, set_request_id

class IntegrationWsgiMiddleware:
    def __init__(self, app, config=Config.default()):
        self.app = app
        self.config = config
        self.connection = Connection(self.config)

    def __call__(self, environ, start_response):
        header = environ.get("HTTP_X_CLIENT_CONTEXT")

        if not header:
            raise ValueError("x-client-context not set")

        set_client_context(ClientContext.from_header(header, self.connection))
        set_request_id(environ.get("HTTP_X_REQUEST_ID", str(uuid.uuid4())))

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

        # Use the Connection's header decoding
        headers = self.connection._decode_headers(dict(scope["headers"]))
        header = headers.get("x-client-context")
        if not header:
            raise ValueError("x-client-context not set")

        set_client_context(ClientContext.from_header(header, self.connection))
        # No b prefix needed since headers are already decoded
        set_request_id(headers.get("x-request-id", str(uuid.uuid4())))

        await self.app(scope, receive, send)
