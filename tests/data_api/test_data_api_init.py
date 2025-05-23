# tests/data_api/test_data_api.py
import pytest
import orjson
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from heroku_applink.data_api import DataAPI, Record, RecordQueryResult, UnitOfWork
from heroku_applink.data_api.exceptions import ClientError, UnexpectedRestApiResponsePayload

@pytest.fixture(autouse=True)
async def clear_cache():
    """Clear any cached responses between tests."""
    yield
    # No need to explicitly clear cache as each test creates its own session
    # and the data_api fixture handles cleanup

@pytest.fixture
async def data_api():
    api = DataAPI(
        org_domain_url="https://example.salesforce.com",
        api_version="v60.0",
        access_token="token"
    )
    yield api
    if api._shared_session:
        await api._shared_session.close()

@pytest.mark.asyncio
async def test_query(data_api):
    result = RecordQueryResult(done=True, total_size=1, records=[], next_records_url=None)
    data_api._execute = AsyncMock(return_value=result)
    response = await data_api.query("SELECT Id FROM Account")
    assert response.done

@pytest.mark.asyncio
async def test_query_more_no_url(data_api):
    result = RecordQueryResult(done=True, total_size=2, records=[], next_records_url=None)
    response = await data_api.query_more(result)
    assert response.total_size == 2

@pytest.mark.asyncio
async def test_create(data_api):
    record = Record(type="Account", fields={"Name": "Test"})
    data_api._execute = AsyncMock(return_value="001123")
    result = await data_api.create(record)
    assert result == "001123"

@pytest.mark.asyncio
async def test_update(data_api):
    record = Record(type="Account", fields={"Id": "001123", "Name": "Updated"})
    data_api._execute = AsyncMock(return_value="001123")
    result = await data_api.update(record)
    assert result == "001123"

@pytest.mark.asyncio
async def test_update_missing_id():
    record = Record(type="Account", fields={"Name": "NoId"})
    from heroku_applink.data_api._requests import UpdateRecordRestApiRequest
    with pytest.raises(Exception):
        UpdateRecordRestApiRequest(record)

@pytest.mark.asyncio
async def test_delete(data_api):
    data_api._execute = AsyncMock(return_value="001123")
    result = await data_api.delete("Account", "001123")
    assert result == "001123"

@pytest.mark.asyncio
async def test_commit_unit_of_work(data_api):
    uow = UnitOfWork()
    ref = uow.register_create(Record(type="Account", fields={"Name": "A"}))
    data_api._execute = AsyncMock(return_value={ref: "001ABC"})
    result = await data_api.commit_unit_of_work(uow)
    assert ref in result

@pytest.mark.asyncio
async def test_unit_of_work_multiple_ops():
    uow = UnitOfWork()
    create_ref = uow.register_create(Record(type="Account", fields={"Name": "A"}))
    update_ref = uow.register_update(Record(type="Account", fields={"Id": "001", "Name": "B"}))
    delete_ref = uow.register_delete("Account", "001")
    assert create_ref != update_ref != delete_ref

@pytest.mark.asyncio
async def test_download_file(data_api):
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b"file-data")
        mock_request.return_value = mock_response
        result = await data_api._download_file("/path")
        assert result == b"file-data"

@pytest.mark.asyncio
async def test_default_headers(data_api):
    headers = data_api._default_headers()
    assert headers["Authorization"] == "Bearer token"

@pytest.mark.asyncio
async def test_create_session():
    from heroku_applink.data_api import _create_session
    session = _create_session()
    assert isinstance(session, aiohttp.ClientSession)
    await session.close()

@pytest.mark.asyncio
async def test_json_serialize():
    from heroku_applink.data_api import _json_serialize
    payload = _json_serialize({"key": "value"})
    assert payload.content_type == "application/json"

@pytest.mark.asyncio
async def test_execute_client_error(data_api):
    mock_req = MagicMock()
    mock_req.url.return_value = "https://fake"
    mock_req.http_method.return_value = "GET"
    mock_req.request_body.return_value = None
    mock_req.process_response = AsyncMock()

    with patch("aiohttp.ClientSession.request", side_effect=aiohttp.ClientError("fail")):
        with pytest.raises(ClientError):
            await data_api._execute(mock_req)

@pytest.mark.asyncio
async def test_execute_with_invalid_json(data_api):
    mock_req = MagicMock()
    mock_req.url.return_value = "https://fake"
    mock_req.http_method.return_value = "GET"
    mock_req.request_body.return_value = None
    mock_req.process_response = AsyncMock()

    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b"not-valid-json")
        mock_request.return_value = mock_response

        with patch("orjson.loads", side_effect=orjson.JSONDecodeError("fail", "bad", 0)):
            with pytest.raises(UnexpectedRestApiResponsePayload):
                await data_api._execute(mock_req)

@pytest.mark.asyncio
async def test_commit_unit_of_work_with_update_and_delete(data_api):
    uow = UnitOfWork()
    update_ref = uow.register_update(Record(type="Account", fields={"Id": "001X", "Name": "Update"}))
    delete_ref = uow.register_delete("Contact", "003Y")
    mock_result = {update_ref: "001X", delete_ref: "003Y"}

    data_api._execute = AsyncMock(return_value=mock_result)
    result = await data_api.commit_unit_of_work(uow)
    assert result[update_ref] == "001X"
    assert result[delete_ref] == "003Y"


@pytest.mark.asyncio
async def test_create_session_cleanup():
    from heroku_applink.data_api import _create_session
    session = _create_session()
    assert isinstance(session, aiohttp.ClientSession)
    await session.close()
    assert session.closed
