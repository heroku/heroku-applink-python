import os
from typing import TypedDict, Optional, Any
import urllib.parse
from heroku_applink.utils.http_request import HttpRequestUtil
from heroku_applink.context import ClientContext, Org, User, DataAPI

http_request_util = HttpRequestUtil()

class RequestOptions(TypedDict):
    method: str
    headers: dict[str, str]
    json: Optional[dict[str, Any]]  # `json` is optional

def resolve_addon_config_by_attachment(attachment: str) -> dict:
    """Resolve the addon configuration by attachment name."""
    api_url = os.getenv(f"{attachment.upper()}_API_URL")
    token = os.getenv(f"{attachment.upper()}_TOKEN")
    if not api_url or not token:
        raise EnvironmentError(f"Missing environment variables for attachment '{attachment}'. Required: API_URL and TOKEN.")
    return {"api_url": api_url, "token": token}

def resolve_addon_config_by_url(url: str) -> dict:
    """Resolve the addon configuration based on the provided URL."""
    for key, value in os.environ.items():
        if key.endswith("_API_URL") and value.lower() == url.lower():
            prefix = key.replace("_API_URL", "")
            token = os.getenv(f"{prefix}_TOKEN")
            if not token:
                raise EnvironmentError(f"Missing token for API URL '{url}'.")
            return {"api_url": value, "token": token}
    raise EnvironmentError(f"Heroku Applink config not found for API URL: {url}")

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def get_authorization(developer_name: str, attachment_name_or_url: Optional[str] = "HEROKU_APPLINK") -> ClientContext:
    """
    Get authorization information for a Heroku Applink developer.

    Args:
        developer_name: The name of the developer to authorize.
        attachment_name_or_url: Optional attachment name or URL.

    Returns:
        ClientContext: A context object containing the authorization information.

    Raises:
        ValueError: If developer_name is empty.
        EnvironmentError: If required environment variables are missing.
        RuntimeError: If the authorization request fails.
    """
    if not developer_name:
        raise ValueError("Developer name must be provided")

    if attachment_name_or_url:
        if validate_url(attachment_name_or_url):
            # If it's a valid URL, resolve config based on URL
            config = resolve_addon_config_by_url(attachment_name_or_url)
        else:
            # Otherwise, resolve config based on attachment name
            config = resolve_addon_config_by_attachment(attachment_name_or_url)
    else:
        # Default behavior if no attachment name or URL is provided
        config = resolve_addon_config_by_attachment("HEROKU_APPLINK")

    auth_url = f"{config['api_url']}/invocations/authorization"
    opts: RequestOptions = {
        "method": "GET",
        "headers": {
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json"
        },
        "json": {"developer_name": developer_name},
    }

    try:
        response = await http_request_util.request(auth_url, opts)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch authorization from {auth_url}: {str(e)}")

    if "message" in response:
        raise RuntimeError(f"Authorization request failed: {response['message']}")

    # Using ClientContext instead of OrgImpl
    org = Org(
        id=response["org_id"],
        domain_url=response["org_domain_url"],
        user=User(id=response["user_id"], username=response["username"])
    )

    client_context = ClientContext(
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

    return client_context
