"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import os

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse, urljoin

from .config import Config
from .connection import Connection
from .data_api import DataAPI


@dataclass(frozen=True, kw_only=True, slots=True)
class AuthBundle:
    """
    A bundle of authentication information for the Salesforce Data API. This
    class should not leak outside of the Authorization class.
    """
    api_url: str
    token: str

@dataclass(frozen=True, kw_only=True, slots=True)
class UserAuth:
    """
    User authentication information for the Salesforce org.
    """
    username: str
    user_id: str
    access_token: str

@dataclass(frozen=True, kw_only=True, slots=True)
class Org:
    """
    Salesforce org information.
    """
    id: str
    developer_name: str
    instance_url: str
    type: str
    api_version: str
    user_auth: UserAuth

@dataclass
class Authorization:
    connection: Connection
    """
    Authorization information for a Salesforce org with access to a Data API for
    making SOQL queries.
    """

    data_api: DataAPI
    """
    An initialized data API client instance for interacting with data in the org.

    Example usage:

    ```python
    authorization = await Authorization.find(developer_name)
    result = await authorization.data_api.query("SELECT Id, Name FROM Account")
    ```
    """

    id: str
    status: str
    org: Org
    created_at: str
    last_modified_at: str
    created_by: str
    last_modified_by: str

    @staticmethod
    async def find(
        developer_name: str,
        attachment_or_url: str|None=None,
        config: Config=Config.default()
    ) -> "Authorization":
        """
        Fetch authorization for a given Heroku AppLink developer.
        Uses GET {apiUrl}/authorizations/{developer_name}
        with a Bearer token from the add-on config.

        This function will raise aiohttp-specific exceptions for HTTP errors and
        any HTTP response other than 200 OK.

        For a list of exceptions, see:
        * https://docs.aiohttp.org/en/stable/client_reference.html
        """

        if not developer_name:
            raise ValueError("Developer name must be provided")

        connection = Connection(config)
        auth_bundle = _resolve_attachment_or_url(attachment_or_url)
        request_url = urljoin(auth_bundle.api_url, f"authorizations/{developer_name}")
        headers = {
            "Authorization": f"Bearer {auth_bundle.token}",
            "Content-Type": "application/json",
        }

        response = await connection.request("GET", request_url, headers=headers)
        payload = await response.json()

        return Authorization._build_authorization(connection, payload)

    @staticmethod
    def _build_authorization(connection: Connection, payload: dict) -> "Authorization":
        return Authorization(
            connection=connection,
            data_api=DataAPI(
                org_domain_url=payload["org"]["instance_url"],
                api_version=payload["org"]["api_version"],
                access_token=payload["org"]["user_auth"]["access_token"],
                connection=connection,
            ),
            id=payload["id"],
            status=payload["status"],
            org=Org(
                id=payload["org"]["id"],
                developer_name=payload["org"]["developer_name"],
                instance_url=payload["org"]["instance_url"],
                type=payload["org"]["type"],
                api_version=payload["org"]["api_version"],
                user_auth=UserAuth(
                    username=payload["org"]["user_auth"]["username"],
                    user_id=payload["org"]["user_auth"]["user_id"],
                    access_token=payload["org"]["user_auth"]["access_token"],
                ),
            ),
            created_at=payload["created_at"],
            last_modified_at=payload["last_modified_at"],
            created_by=payload["created_by"],
            last_modified_by=payload["last_modified_by"],
        )


def _resolve_attachment_or_url(attachment_or_url: Optional[str] = None) -> AuthBundle:
   if attachment_or_url:
      if _is_valid_url(attachment_or_url):
         return _resolve_addon_config_by_url(attachment_or_url)
      else:
         return _resolve_addon_config_by_attachment_or_color(attachment_or_url)
   else:
      return _resolve_addon_config_by_attachment_or_color("HEROKU_APPLINK")

def _is_valid_url(url: str) -> bool:
    result = urlparse(url)
    return all([result.scheme, result.netloc])

@lru_cache(maxsize=None)
def _resolve_addon_config_by_attachment_or_color(attachment_or_color: str) -> AuthBundle:
    """
    First try:
      {ATTACHMENT}_API_URL / _TOKEN
    Then fallback to:
      HEROKU_APPLINK_{COLOR}_API_URL / _TOKEN
    """
    addon_prefix = os.getenv("HEROKU_APPLINK_ADDON_NAME", "HEROKU_APPLINK")
    key = attachment_or_color.upper()

    api_url = os.getenv(f"{key}_API_URL")
    token   = os.getenv(f"{key}_TOKEN")

    if not api_url or not token:
        # fallback: color under the main addon prefix
        api_url = os.getenv(f"{addon_prefix}_{key}_API_URL")
        token   = os.getenv(f"{addon_prefix}_{key}_TOKEN")

    if not api_url or not token:
        raise EnvironmentError(
            f"Heroku Applink config not found for '{attachment_or_color}'. "
            f"Looked for {key}_API_URL / {key}_TOKEN and "
            f"{addon_prefix}_{key}_API_URL / {addon_prefix}_{key}_TOKEN"
        )

    return AuthBundle(api_url=api_url, token=token)

@lru_cache(maxsize=None)
def _resolve_addon_config_by_url(url: str) -> AuthBundle:
    """
    Match an env var ending in _API_URL to the given URL, then
    pull the corresponding _TOKEN.
    """
    for var, val in os.environ.items():
        if var.endswith("_API_URL") and val.lower() == url.lower():
            prefix = var[: -len("_API_URL")]
            token = os.getenv(f"{prefix}_TOKEN")

            if not token:
                raise EnvironmentError(f"Missing token for API URL: {url}")

            return AuthBundle(api_url=val, token=token)

    raise EnvironmentError(f"Heroku Applink config not found for API URL: {url}")
