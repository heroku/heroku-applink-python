import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../heroku_applink')))

import pytest
from unittest.mock import MagicMock, AsyncMock
from heroku_applink.data_api import DataAPI, Record, ClientError, UnexpectedRestApiResponsePayload
from heroku_applink.exceptions import ClientError
from aiohttp import ClientResponse


@pytest.fixture
def mock_session(mocker):
    """Fixture to mock aiohttp ClientSession."""
    return mocker.patch("heroku_applink.data_api.aiohttp.ClientSession", autospec=True)

@pytest.fixture
def data_api(mock_session):
    """Fixture to instantiate the DataAPI class with mock session."""
    return DataAPI(
        org_domain_url="https://example.salesforce.com",
        api_version="v52.0",
        access_token="mock-access-token",
        session=mock_session(),
    )


# Test query method
@pytest.mark.asyncio
async def test_query(data_api, mocker):
    mock_response = {
        "records": [{"Id": "001B000001Lp1FxIAJ", "Name": "Test Account"}],
        "done": True,
        "totalSize": 1,
    }

    mocker.patch.object(data_api, "_execute", return_value=mock_response)

    soql_query = "SELECT Id, Name FROM Account"
    result = await data_api.query(soql_query)

    assert result["records"][0]["Id"] == "001B000001Lp1FxIAJ"
    assert result["records"][0]["Name"] == "Test Account"
    assert result["done"] is True

# Test create method
@pytest.mark.asyncio
async def test_create(data_api, mocker):
    record = Record(type="Account", fields={"Name": "Test Account"})
    mocker.patch.object(data_api, "_execute", return_value="001B000001Lp1FxIAJ")

    record_id = await data_api.create(record)

    assert record_id == "001B000001Lp1FxIAJ"


# Test update method
@pytest.mark.asyncio
async def test_update(data_api, mocker):
    record = Record(type="Account", fields={"Id": "001B000001Lp1FxIAJ", "Name": "Updated Account"})
    mocker.patch.object(data_api, "_execute", return_value="001B000001Lp1FxIAJ")

    record_id = await data_api.update(record)

    assert record_id == "001B000001Lp1FxIAJ"


# Test delete method
@pytest.mark.asyncio
async def test_delete(data_api, mocker):
    mocker.patch.object(data_api, "_execute", return_value="001B000001Lp1FxIAJ")

    record_id = await data_api.delete("Account", "001B000001Lp1FxIAJ")

    assert record_id == "001B000001Lp1FxIAJ"


# Test commit_unit_of_work method
@pytest.mark.asyncio
async def test_commit_unit_of_work(data_api, mocker):
    unit_of_work = MagicMock()
    mocker.patch.object(data_api, "_execute", return_value={})

    result = await data_api.commit_unit_of_work(unit_of_work)

    assert result == {}


# Test exception handling on ClientError
@pytest.mark.asyncio
async def test_client_error(data_api, mocker):
    mocker.patch.object(data_api, "_execute", side_effect=ClientError("Client error"))

    with pytest.raises(ClientError):
        await data_api.query("SELECT Id, Name FROM Account")


# Test exception handling on UnexpectedRestApiResponsePayload
@pytest.mark.asyncio
async def test_unexpected_response(data_api, mocker):
    mocker.patch.object(data_api, "_execute", side_effect=UnexpectedRestApiResponsePayload("Invalid response"))

    with pytest.raises(UnexpectedRestApiResponsePayload):
        await data_api.query("SELECT Id, Name FROM Account")
