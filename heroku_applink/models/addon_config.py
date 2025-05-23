from dataclasses import dataclass

@dataclass
class AddOnConfig:
    """Configuration for a Heroku add-on."""
    api_url: str
    token: str
