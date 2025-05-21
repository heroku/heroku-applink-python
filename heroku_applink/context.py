import json
import base64
import aiohttp
from dataclasses import dataclass

from .config import Config
from .data_api import DataAPI

__all__ = ["User", "Org", "ClientContext"]


@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    """
    Information about the Salesforce user that made the request.
    """

    id: str
    """
    The user's ID.

    For example: `005JS000000H123`
    """
    username: str
    """
    The username of the user.

    For example: `user@example.tld`
    """


@dataclass(frozen=True, kw_only=True, slots=True)
class Org:
    """Information about the Salesforce org and the user that made the request."""

    id: str
    """
    The Salesforce org ID.

    For example: `00DJS0000000123ABC`
    """

    domain_url: str
    """
    The canonical URL of the Salesforce org.

    This URL never changes. Use this URL when making API calls to your org.

    For example: `https://example-domain-url.my.salesforce.com`
    """
    user: User
    """The currently logged in user."""


@dataclass(frozen=True, kw_only=True, slots=True)
class ClientContext:
    """Information about the Salesforce org that made the request."""

    org: Org
    """Information about the Salesforce org and the user that made the request."""
    data_api: DataAPI
    """An initialized data API client instance for interacting with data in the org."""
    request_id: str
    """Request ID from the Salesforce org."""
    access_token: str
    """Valid access token for the current context org/user."""
    api_version: str
    """API version of the Salesforce component that made the request."""
    namespace: str
    """Namespace of the Salesforce component that made the request."""

    @classmethod
    def from_header(cls, header: str, session: aiohttp.ClientSession):
        decoded = base64.b64decode(header)
        data = json.loads(decoded)

        return cls(
            org=Org(
                id=data["orgId"],
                domain_url=data["orgDomainUrl"],
                user=User(
                    id=data["userContext"]["userId"],
                    username=data["userContext"]["username"],
                ),
            ),
            request_id=data["requestId"],
            access_token=data["accessToken"],
            api_version=data["apiVersion"],
            namespace=data["namespace"],
            data_api=DataAPI(
                org_domain_url=data["orgDomainUrl"],
                api_version=data["apiVersion"],
                access_token=data["accessToken"],
                session=session,
            ),
        )
