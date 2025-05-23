from dataclasses import dataclass
from enum import Enum
from .user import User

class OrgType(str, Enum):
    """The type of the org."""
    SALESFORCE = "SalesforceOrg"
    DATACLOUD = "DataCloudOrg"
    DATACLOUD_LEGACY = "DatacloudOrg"  # Legacy Pilot/Ruby

@dataclass(frozen=True, kw_only=True, slots=True)
class Org:
    """Information about the Salesforce org and the user that made the request."""
    id: str
    domain_url: str
    user: User
    type: OrgType
