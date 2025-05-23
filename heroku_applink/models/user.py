from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    """
    Information about the Salesforce user that made the request.
    """
    id: str
    username: str
