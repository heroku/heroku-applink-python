import asyncio
import heroku_applink as sdk
from fastapi import FastAPI

config = sdk.Config(request_timeout=5)

app = FastAPI()
app.add_middleware(sdk.IntegrationAsgiMiddleware, config=config)

@app.get("/")
def get_root():
    return {"root": "page"}


@app.get("/accounts")
def get_accounts():
    data_api = sdk.get_client_context().data_api
    result = asyncio.run(query_accounts(data_api))
    
    accounts = [
        {
            "id": record.fields["Id"],
            "name": record.fields["Name"]
        }
        for record in result.records
    ]
    return accounts


async def query_accounts(data_api):
    query = "SELECT Id, Name FROM Account"
    result = await data_api.query(query)
    for record in result.records:
        print("===== account record", record)
    return result
