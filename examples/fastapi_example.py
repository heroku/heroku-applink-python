import asyncio
from heroku_applink import IntegrationAsgiMiddleware, client_context
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(IntegrationAsgiMiddleware)


@app.get("/")
def get_root():
    return {"root": "page"}


@app.get("/accounts")
def get_accounts():
    context = client_context.get()
    dataapi = context.data_api    
    asyncio.run(query_accounts(dataapi))
    return {"Some": "Accounts"}


async def query_accounts(dataapi):
    query = "SELECT Id, Name FROM Account"
    result = await dataapi.query(query)
    for record in result.records:
        print("===== account record", record)
