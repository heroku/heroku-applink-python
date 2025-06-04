"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import aiohttp
import orjson

from datetime import datetime
from dataclasses import dataclass
from typing import Any
from aiohttp.payload import BytesPayload

from .connection import Connection

@dataclass(frozen=True, kw_only=True, slots=True)
class Metadata:
    type: str
    place_in_order: int
    type_code: int

@dataclass(frozen=True, kw_only=True, slots=True)
class Results:
    """
    Represents a [Data Cloud Query API](https://developer.salesforce.com/docs/atlas.en-us.c360a_api.meta/c360a_api/c360a_api_query_v2.htm) response.
    """

    data: list[Any]
    start_time: datetime
    end_time: datetime
    row_count: int
    query_id: str
    next_batch_id: str|None
    done: bool
    metadata: dict[str, Metadata]


class DataCloudAPI:
    """
    A client for the Salesforce Data Cloud API.
    """

    def __init__(self, org_domain_url: str, access_token: str, connection: Connection):
        self.org_domain_url = org_domain_url
        self.access_token = access_token
        self.connection = connection

    async def query(self, query: str, timeout: float|None=None):
        """
        Execute a query against the Data Cloud API.
        """
        url = f"{self.org_domain_url}/api/v2/query"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = await self.connection.request(
            "POST",
            url,
            headers=headers,
            data=_json_serialize({"sql": query}),
            timeout=timeout,
        )

        return await _parse_data_cloud_query_response(response)


async def _parse_data_cloud_query_response(response: aiohttp.ClientResponse) -> Results:
    """
    Parse a Data Cloud Query API response into a DataCloud Results object.
    """
    payload = await response.json()

    # TODO: parse the response into a Results object
    # TODO: make sure the response is valid (200 OK)
    # TODO: handle errors
    # TODO: parse start_time/end_time into datetime objects
    # TODO: support pagination from next_batch_id

    return Results(
        data=payload["data"],
        start_time=payload["startTime"],
        end_time=payload["endTime"],
        row_count=payload["rowCount"],
        query_id=payload["queryId"],
        next_batch_id=payload["nextBatchId"],
        done=payload["done"],
        metadata=payload["metadata"],
    )

def _json_serialize(data: Any) -> BytesPayload:
    """
    JSON serialize the provided data to bytes.

    This is a replacement for aiohttp's default JSON implementation that uses `orjson` instead
    of the Python stdlib's `json` module, since `orjson` is faster:
    https://github.com/ijl/orjson#performance

    We can't just implement this by passing `json_serialize` to `ClientSession`, due to:
    https://github.com/aio-libs/aiohttp/issues/4482

    So instead this is based on `payload.JsonPayload`:
    https://github.com/aio-libs/aiohttp/blob/v3.8.3/aiohttp/payload.py#L386-L403
    """
    return BytesPayload(
        orjson.dumps(data), encoding="utf-8", content_type="application/json"
    )
