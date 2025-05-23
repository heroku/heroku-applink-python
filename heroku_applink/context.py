import json
import base64
from dataclasses import dataclass, field
from .data_api import DataAPI
from .addons import heroku_applink
from .models import Org, User, OrgType

__all__ = ["User", "Org", "ClientContext", "OrgType"]

@dataclass(frozen=True, kw_only=True, slots=True)
class ClientContext:
    """Information about the Salesforce org that made the request."""
    org: Org
    data_api: DataAPI
    request_id: str
    access_token: str
    api_version: str
    namespace: str
    addons: object = field(default_factory=lambda: type('Addons', (), {
        'heroku_integration': heroku_applink
    }))

    @classmethod
    def from_header(cls, header: str):
        decoded = base64.b64decode(header)
        data = json.loads(decoded)

        org_type = data.get("orgType", "SalesforceOrg")
        try:
            org_type = OrgType(org_type)
        except ValueError:
            org_type = OrgType.SALESFORCE

        return cls(
            org=Org(
                id=data["orgId"],
                domain_url=data["orgDomainUrl"],
                user=User(
                    id=data["userContext"]["userId"],
                    username=data["userContext"]["username"],
                ),
                type=OrgType.SALESFORCE,
            ),
            request_id=data["requestId"],
            access_token=data["accessToken"],
            api_version=data["apiVersion"],
            namespace=data["namespace"],
            data_api=DataAPI(
                org_domain_url=data["orgDomainUrl"],
                api_version=data["apiVersion"],
                access_token=data["accessToken"],
            ),
        )
