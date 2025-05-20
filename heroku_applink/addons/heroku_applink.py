import urllib.parse
from typing import TypedDict, Optional
from heroku_applink.utils.http_request import HttpRequestUtil
from heroku_applink.context import ClientContext, Org, User, DataAPI
from heroku_applink.utils.addon_config import (
    resolve_addon_config_by_attachment_or_color,
    resolve_addon_config_by_url,
)

http_request_util = HttpRequestUtil()

class RequestOptions(TypedDict):
    method: str
    headers: dict[str, str]

async def get_authorization(
    developer_name: str,
    attachment_or_url: Optional[str] = None,
) -> ClientContext:
    """
    Parity with the Node.js getAuthorization, but using GET:

      GET {apiUrl}/invocations/authorization?org_name=developer_name
    """
    if not developer_name:
        raise ValueError("Developer name must be provided")

    # determine config
    if attachment_or_url:
        is_url = False
        try:
            parts = urllib.parse.urlparse(attachment_or_url)
            is_url = all([parts.scheme, parts.netloc])
        except ValueError:
            pass

        config = (
            resolve_addon_config_by_url(attachment_or_url)
            if is_url
            else resolve_addon_config_by_attachment_or_color(attachment_or_url)
        )
    else:
        config = resolve_addon_config_by_attachment_or_color("HEROKU_APPLINK")

    # build GET URL with query param
    base = config["api_url"].rstrip("/")
    qs   = urllib.parse.urlencode({"org_name": developer_name})
    full_url = f"{base}/invocations/authorization?{qs}"

    opts: RequestOptions = {
        "method": "GET",
        "headers": {
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json",
        },
    }

    try:
        response = await http_request_util.request(full_url, opts)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch authorization from {full_url}: {e}")

    if response.get("message"):
        raise RuntimeError(f"Authorization request failed: {response['message']}")

    # hydrate ClientContext just like Node.js does
    org = Org(
        id=response["org_id"],
        domain_url=response["org_domain_url"],
        user=User(id=response["user_id"], username=response["username"]),
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
