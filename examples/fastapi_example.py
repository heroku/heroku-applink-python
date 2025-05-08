import asyncio
import heroku_applink as sdk
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(sdk.IntegrationAsgiMiddleware)


@app.get("/")
def get_root():
    return {"root": "page"}


@app.get("/accounts")
def get_accounts():
    dataapi = sdk.context.get()
    asyncio.run(query_accounts(dataapi))
    return {"Some": "Accounts"}


async def query_accounts(dataapi):
    query = "SELECT Id, Name FROM Account"
    result = await dataapi.query(query)
    for record in result.records:
        print("===== account record", record)
