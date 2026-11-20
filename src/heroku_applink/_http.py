# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import http.client
import ssl
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from urllib.parse import SplitResult

from ._errors import ConfigurationError, TransportError

MAX_BODY_BYTES = 1024 * 1024


@dataclass(frozen=True, slots=True)
class HttpSettings:
    timeout: float = 5.0
    retry_delays: Sequence[float] = (0.25, 0.5, 1.0)
    ssl_context: ssl.SSLContext = field(default_factory=ssl.create_default_context)


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    body: bytes
    body_too_large: bool


def get_with_retries(
    url: SplitResult, path: str, headers: Mapping[str, str], settings: HttpSettings
) -> HttpResponse:
    attempt = 0
    while True:
        result: HttpResponse | TransportError
        try:
            result = _get(url, path, headers, settings)
        except TransportError as error:
            result = error

        if attempt >= len(settings.retry_delays) or not _is_retryable(result):
            if isinstance(result, TransportError):
                raise result
            return result
        time.sleep(settings.retry_delays[attempt])
        attempt += 1


def _is_retryable(result: HttpResponse | TransportError) -> bool:
    if isinstance(result, TransportError):
        return True
    return result.status == 429 or 500 <= result.status <= 599


def _get(
    url: SplitResult, path: str, headers: Mapping[str, str], settings: HttpSettings
) -> HttpResponse:
    deadline = time.monotonic() + settings.timeout
    connection = http.client.HTTPSConnection(
        url.hostname or "",
        url.port,
        timeout=settings.timeout,
        context=settings.ssl_context,
    )

    def limit_to_deadline() -> None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        if connection.sock is not None:
            connection.sock.settimeout(remaining)

    try:
        connection.putrequest("GET", path)
        for name, value in headers.items():
            connection.putheader(name, value)
    except (ValueError, http.client.InvalidURL):
        connection.close()
        # Raised without the cause, because its message can contain the token.
        raise ConfigurationError(
            "The config vars don't form a valid AppLink API request."
        ) from None

    try:
        connection.connect()
        limit_to_deadline()
        connection.endheaders()
        limit_to_deadline()
        response = connection.getresponse()
        chunks: list[bytes] = []
        length = 0
        while length <= MAX_BODY_BYTES:
            limit_to_deadline()
            chunk = response.read1(MAX_BODY_BYTES + 1 - length)
            if not chunk:
                break
            chunks.append(chunk)
            length += len(chunk)
        body = b"".join(chunks)
        return HttpResponse(
            status=response.status,
            body=body[:MAX_BODY_BYTES],
            body_too_large=len(body) > MAX_BODY_BYTES,
        )
    except TimeoutError as error:
        raise TransportError("The request to the AppLink API timed out.") from error
    except (OSError, UnicodeError, http.client.HTTPException) as error:
        raise TransportError(
            f"The request to the AppLink API failed: {type(error).__name__}: {error}"
        ) from error
    finally:
        connection.close()
