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
from .context import ClientContext, Org, User
from .data_api import DataAPI

@dataclass
class AuthBundle:
    """
    A bundle of authentication information for the Salesforce Data API. This
    class should not leak outside of the Authorization class.
    """
    api_url: str
    token: str


class Authorization:
  def __init__(self, config: Config):
    self.config = config
    self.connection = Connection(self.config)

  async def get_client_context(self) -> ClientContext:
    """
    Fetch authorization for a given Heroku AppLink developer.
    Uses GET {apiUrl}/authorizations/{developer_name}
    with a Bearer token from the add-on config.

    For a list of exceptions, see:
      * https://docs.aiohttp.org/en/stable/client_reference.html
    """

    if not self.config.developer_name:
        raise ValueError("Developer name must be provided")

    auth_bundle = _resolve_attachment_or_url(self.config.attachment_or_url)
    request_url = urljoin(
       auth_bundle.api_url,
       f"authorizations/{self.config.developer_name}"
    )
    headers = {
       "Authorization": f"Bearer {auth_bundle.token}",
       "Content-Type": "application/json",
    }

    response = await self.connection.request("GET", request_url, headers=headers)
    payload = await response.json()

    return self._build_client_context(payload)

  def _build_client_context(self, response: dict) -> ClientContext:
    return ClientContext(
        org=Org(
            id=response["org_id"],
            domain_url=response["org_domain_url"],
            user=User(id=response["user_id"], username=response["username"]),
        ),
        request_id=response["request_id"],
        access_token=response["access_token"],
        api_version=response["api_version"],
        namespace=response["namespace"],
        data_api=DataAPI(
            org_domain_url=response["org_domain_url"],
            api_version=response["api_version"],
            access_token=response["access_token"],
            connection=self.connection,
        ),
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
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

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
