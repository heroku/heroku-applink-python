# heroku_applink/utils/http_request.py

import aiohttp

class HttpRequestUtil:
    async def request(self, url: str, opts: dict, return_json: bool = True):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=opts.get("method", "GET"),
                url=url,
                headers=opts.get("headers"),
                json=opts.get("json"),
                data=opts.get("body"),
            ) as response:
                if return_json:
                    return await response.json()
                return await response.read()
