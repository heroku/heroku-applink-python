# heroku_applink/addons/heroku_applink.py

import os
from heroku_applink.utils.http_request import HttpRequestUtil
from heroku_applink.context import Org, User

http_request_util = HttpRequestUtil()

async def get_authorization(developer_name: str, attachment_name_or_url: str | None = None) -> Org:
    if not developer_name:
        raise ValueError("Developer name must be provided")

    if attachment_name_or_url:
        if attachment_name_or_url.startswith("http"):
            addon_endpoint = attachment_name_or_url
            addon_token = os.getenv("HEROKU_APPLINK_TOKEN")  # Still needs a token
        else:
            key = attachment_name_or_url.upper()
            addon_endpoint = os.getenv(f"HEROKU_APPLINK_{key}_API_URL")
            addon_token = os.getenv(f"HEROKU_APPLINK_{key}_TOKEN")
            if not addon_endpoint or not addon_token:
                raise EnvironmentError(
                    f"Missing environment variables for attachment '{attachment_name_or_url}'"
                )
    else:
        addon_endpoint = os.getenv("HEROKU_APPLINK_API_URL") or os.getenv("HEROKU_APPLINK_STAGING_API_URL")
        addon_token = os.getenv("HEROKU_APPLINK_TOKEN")

    if not addon_endpoint or not addon_token:
        raise EnvironmentError("Heroku Applink endpoint or token not configured")

    auth_url = f"{addon_endpoint}/invocations/authorization"
    opts = {
        "method": "POST",
        "headers": {
            "Authorization": f"Bearer {addon_token}",
            "Content-Type": "application/json"
        },
        "json": {"org_name": developer_name},
    }

    try:
        response = await http_request_util.request(auth_url, opts)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch authorization: {str(e)}")

    if "message" in response:
        raise RuntimeError(response["message"])

    return Org(
        id=response["org_id"],
        domain_url=response["org_domain_url"],
        user=User(id=response["user_id"], username=response["username"])
    )
