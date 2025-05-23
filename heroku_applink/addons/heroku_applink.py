import asyncio
import urllib.parse
from typing import TypedDict, Optional, TYPE_CHECKING
from heroku_applink.utils.http_request import HttpRequestUtil
from heroku_applink.models import Org, User
from heroku_applink.context import DataAPI
from heroku_applink.utils.addon_config import (
    resolve_addon_config_by_attachment_or_color,
    resolve_addon_config_by_url,
)
import os

http_request_util = HttpRequestUtil()

class RequestOptions(TypedDict):
    method: str
    headers: dict[str, str]

# How long to wait for the add-on call before giving up (in seconds)
try:
    HTTP_TIMEOUT_SECONDS = float(os.getenv("HEROKU_APPLINK_TIMEOUT", "5.0"))
except ValueError:
    HTTP_TIMEOUT_SECONDS = 5.0

# Fields we expect in a successful authorization payload
_REQUIRED_FIELDS = {
    "org_id",
    "org_domain_url",
    "user_id",
    "username",
    "request_id",
    "access_token",
    "api_version",
    "namespace",
}

if TYPE_CHECKING:
    from heroku_applink.context import ClientContext

async def get_authorization(
    developer_name: str,
    attachment_or_url: Optional[str] = None,
) -> 'ClientContext':
    from heroku_applink.context import ClientContext
    """
    Fetch authorization for a given Heroku AppLink developer.
    Uses GET {apiUrl}/authorizations/{developer_name}
    with a Bearer token from the add-on config.
    """

    if not developer_name:
        raise ValueError("Developer name must be provided")

    # 1) Resolve add-on config (api_url + token), deciding if input is URL vs name/color
    if attachment_or_url:
        # robust URL check: only allow http or https
        parts = urllib.parse.urlparse(attachment_or_url)
        is_url = parts.scheme in ("http", "https") and bool(parts.netloc)

        config = (
            resolve_addon_config_by_url(attachment_or_url)
            if is_url
            else resolve_addon_config_by_attachment_or_color(attachment_or_url)
        )
    else:
        config = resolve_addon_config_by_attachment_or_color("HEROKU_APPLINK")

    # 2) Build the full request URL (strip any trailing slash)
    base = config["api_url"].rstrip("/")
    full_url = f"{base}/authorizations/{developer_name}"

    opts: RequestOptions = {
        "method": "GET",
        "headers": {
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json",
        },
    }

    # 3) Perform the request with a timeout
    try:
        response = await asyncio.wait_for(
            http_request_util.request(full_url, opts),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        raise RuntimeError(f"Authorization request to {full_url} timed out after {HTTP_TIMEOUT_SECONDS}s")
    except Exception as e:
        # Be careful not to include opts (credentials) in the message
        raise RuntimeError(f"Failed to fetch authorization from {full_url}: {e}")

    # 4) Handle an error message in the response
    if isinstance(response, dict) and "message" in response:
        raise RuntimeError(f"Authorization request failed: {response['message']}")

    # 5) Validate presence of required fields
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected authorization payload type")
    missing = _REQUIRED_FIELDS - response.keys()
    if missing:
        raise RuntimeError(f"Authorization payload missing fields: {sorted(missing)}")

    # 6) Hydrate domain objects
    org = Org(
        id=response["org_id"],
        domain_url=response["org_domain_url"],
        user=User(
            id=response["user_id"],
            username=response["username"],
        ),
        type=response["org_type"],
    )

    return ClientContext(
        org=org,
        request_id=response["request_id"],
        access_token=response["access_token"],
        api_version=response["api_version"],
        namespace=response["namespace"],
        data_api=DataAPI(
            org_domain_url=response["org_domain_url"],
            api_version=response["api_version"],
            access_token=response["access_token"],
        ),
    )
