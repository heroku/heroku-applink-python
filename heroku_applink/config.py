from dataclasses import dataclass
import aiohttp


@dataclass
class Config:
    session: aiohttp.ClientSession

    @classmethod
    def default(cls) -> "Config":
        return cls(session=aiohttp.ClientSession(
            cookie_jar=aiohttp.DummyCookieJar(),
            timeout=aiohttp.ClientTimeout(total=5),
        ))
