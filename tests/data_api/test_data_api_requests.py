import pytest
from unittest.mock import AsyncMock

from heroku_applink.data_api._requests import (
    CreateRecordRestApiRequest,
    DeleteRecordRestApiRequest,
    UpdateRecordRestApiRequest,
    QueryRecordsRestApiRequest,
    QueryNextRecordsRestApiRequest,
    CompositeGraphRestApiRequest,
    _normalize_field_value, _normalize_record_fields,
    _is_binary_field, _parse_errors, _process_records_response,
    _parse_record_query_result, _parse_queried_record
)
from heroku_applink.data_api.record import Record
from heroku_applink.data_api.reference_id import ReferenceId
from heroku_applink.data_api.exceptions import (
    UnexpectedRestApiResponsePayload, InnerSalesforceRestApiError, SalesforceRestApiError
)


# Basic request tests
@pytest.mark.asyncio
async def test_create_record_request():
    rec = Record(type="Account", fields={"Name": "Test"})
    req = CreateRecordRestApiRequest(rec)
    assert req.http_method() == "POST"
    assert req.request_body() == {"Name": "Test"}

@pytest.mark.asyncio
async def test_update_record_request():
    rec = Record(type="Account", fields={"Id": "abc", "Name": "Updated"})
    req = UpdateRecordRestApiRequest(rec)
    assert req.http_method() == "PATCH"
    assert req.request_body() == {"Name": "Updated"}

@pytest.mark.asyncio
async def test_delete_record_request():
    req = DeleteRecordRestApiRequest("Account", "123")
    assert req.http_method() == "DELETE"
    assert req.request_body() is None

@pytest.mark.asyncio
async def test_query_record_request():
    req = QueryRecordsRestApiRequest("SELECT Id FROM Account", lambda url: b"")
    assert req.http_method() == "GET"
    assert req.request_body() is None

@pytest.mark.asyncio
async def test_query_next_record_request():
    req = QueryNextRecordsRestApiRequest("/next", lambda url: b"")
    assert req.http_method() == "GET"
    assert req.request_body() is None


# Field utils
def test_normalize_field_value_reference_id():
    ref = ReferenceId(id="ref1")
    assert _normalize_field_value(ref) == "@{ref1.id}"

def test_normalize_field_value_bytes():
    assert _normalize_field_value(b"abc") == "YWJj"

def test_normalize_field_value_default():
    assert _normalize_field_value(123) == 123

def test_normalize_record_fields():
    ref = ReferenceId(id="ref2")
    result = _normalize_record_fields({"key1": b"data", "key2": ref})
    assert result["key1"] == "ZGF0YQ=="
    assert result["key2"] == "@{ref2.id}"

def test_is_binary_field_true():
    assert _is_binary_field("ContentVersion", "VersionData")

def test_is_binary_field_false():
    assert not _is_binary_field("Account", "Name")


# Error parsing
def test_parse_errors_valid_list():
    errors = [
        {"message": "msg", "errorCode": "400", "fields": ["Name"]},
        {"message": "another", "errorCode": "401"}
    ]
    parsed = _parse_errors(errors)
    assert isinstance(parsed[0], InnerSalesforceRestApiError)
    assert parsed[1].fields == []

def test_parse_errors_invalid_type():
    with pytest.raises(UnexpectedRestApiResponsePayload):
        _parse_errors({"not": "a list"})


# Record parsing
@pytest.mark.asyncio
async def test_process_records_response_invalid_type():
    with pytest.raises(UnexpectedRestApiResponsePayload):
        await _process_records_response(200, "not-a-dict", lambda x: b"")

@pytest.mark.asyncio
async def test_parse_record_query_result_basic():
    json_body = {
        "done": True,
        "totalSize": 1,
        "records": [
            {"attributes": {"type": "Account"}, "Name": "Test"}
        ]
    }
    result = await _parse_record_query_result(json_body, lambda x: b"")
    assert result.total_size == 1
    assert result.records[0].fields["Name"] == "Test"

@pytest.mark.asyncio
async def test_parse_queried_record_binary_field():
    json_body = {
        "attributes": {"type": "ContentVersion"},
        "VersionData": "/binary/url"
    }

    async def mock_download(url):
        return b"binary-content"

    result = await _parse_queried_record(json_body, mock_download)
    assert result.fields["VersionData"] == b"binary-content"


# CompositeGraphRestApiRequest edge cases
@pytest.mark.asyncio
async def test_composite_graph_response_error_propagation():
    ref_id = ReferenceId(id="ref-1")
    sub_request = AsyncMock()
    sub_request.url.return_value = "/fake"
    sub_request.http_method.return_value = "POST"
    sub_request.request_body.return_value = {"key": "value"}
    sub_request.process_response.side_effect = SalesforceRestApiError(api_errors=[])

    req = CompositeGraphRestApiRequest("60.0", {ref_id: sub_request})

    error_payload = [
        {
            "message": "Invalid input",
            "errorCode": "INVALID_INPUT",
            "fields": ["Name"]
        }
    ]

    with pytest.raises(SalesforceRestApiError) as exc_info:
        await req.process_response(400, error_payload)

    assert "INVALID_INPUT" in str(exc_info.value)
    assert "Invalid input" in str(exc_info.value)

@pytest.mark.asyncio
async def test_composite_graph_invalid_structure():
    ref_id = ReferenceId(id="r1")
    sub_request = AsyncMock()
    sub_request.url.return_value = "/fake"
    sub_request.http_method.return_value = "POST"
    sub_request.request_body.return_value = {"foo": "bar"}
    sub_request.process_response = AsyncMock()

    req = CompositeGraphRestApiRequest("60.0", {ref_id: sub_request})

    with pytest.raises(UnexpectedRestApiResponsePayload):
        await req.process_response(200, [])

@pytest.mark.asyncio
async def test_query_records_url():
    soql = "SELECT Id, Name FROM Account"
    req = QueryRecordsRestApiRequest(soql, download_file_fn=lambda x: b"")  # dummy download fn

    org_domain_url = "https://example.salesforce.com"
    api_version = "60.0"

    expected_url = "https://example.salesforce.com/services/data/v60.0/query?q=SELECT+Id%2C+Name+FROM+Account"
    assert req.url(org_domain_url, api_version) == expected_url

@pytest.mark.asyncio
async def test_create_record_process_response_success():
    record = Record(type="Account", fields={"Name": "Test"})
    req = CreateRecordRestApiRequest(record)

    status_code = 201
    json_body = {"id": "001XYZ"}

    result = await req.process_response(status_code, json_body)
    assert result == "001XYZ"


@pytest.mark.asyncio
async def test_create_record_process_response_non_201():
    record = Record(type="Account", fields={"Name": "Test"})
    req = CreateRecordRestApiRequest(record)

    status_code = 400
    json_body = [
        {
            "message": "Invalid field",
            "errorCode": "INVALID_FIELD",
            "fields": ["Name"]
        }
    ]

    with pytest.raises(SalesforceRestApiError) as exc:
        await req.process_response(status_code, json_body)

    assert "INVALID_FIELD" in str(exc.value)


@pytest.mark.asyncio
async def test_create_record_process_response_invalid_structure():
    record = Record(type="Account", fields={"Name": "Test"})
    req = CreateRecordRestApiRequest(record)

    status_code = 201
    json_body = "not-a-dict"  # Should trigger UnexpectedRestApiResponsePayload

    with pytest.raises(UnexpectedRestApiResponsePayload):
        await req.process_response(status_code, json_body)

@pytest.mark.asyncio
async def test_update_record_process_response_success():
    record = Record(type="Account", fields={"Id": "001ABC", "Name": "Updated"})
    req = UpdateRecordRestApiRequest(record)

    status_code = 204
    json_body = None  # Body isn't used when status code is 204

    result = await req.process_response(status_code, json_body)
    assert result == "001ABC"


@pytest.mark.asyncio
async def test_update_record_process_response_failure():
    record = Record(type="Account", fields={"Id": "001XYZ", "Name": "BadData"})
    req = UpdateRecordRestApiRequest(record)

    status_code = 400
    json_body = [
        {
            "message": "Field error",
            "errorCode": "INVALID_FIELD",
            "fields": ["Name"]
        }
    ]

    with pytest.raises(SalesforceRestApiError) as exc_info:
        await req.process_response(status_code, json_body)

    assert "INVALID_FIELD" in str(exc_info.value)

@pytest.mark.asyncio
async def test_process_response_dict_json_body_success():
    # Setup a reference ID and a mock sub-request
    ref_id = ReferenceId(id="r1")
    mock_sub_request = AsyncMock()
    mock_sub_request.process_response = AsyncMock(return_value="success-id")

    # Create CompositeGraphRestApiRequest
    request = CompositeGraphRestApiRequest("60.0", {ref_id: mock_sub_request})

    # json_body is a dict → should trigger the isinstance condition
    json_body = {
        "graphs": [{
            "graphResponse": {
                "compositeResponse": [
                    {
                        "referenceId": "r1",
                        "httpStatusCode": 200,
                        "body": {"id": "success-id"}
                    }
                ]
            }
        }]
    }

    result = await request.process_response(200, json_body)
    assert result[ref_id] == "success-id"
    mock_sub_request.process_response.assert_awaited_once_with(200, {"id": "success-id"})

@pytest.mark.asyncio
async def test_process_response_non_dict_json_body():
    ref_id = ReferenceId(id="r1")
    mock_sub_request = AsyncMock()
    request = CompositeGraphRestApiRequest("60.0", {ref_id: mock_sub_request})

    # json_body is a list, so isinstance(json_body, dict) will be False
    json_body = [{"invalid": "structure"}]

    with pytest.raises(UnexpectedRestApiResponsePayload):
        await request.process_response(200, json_body)

@pytest.mark.asyncio
async def test_process_records_response_error_path():
    with pytest.raises(SalesforceRestApiError):
        await _process_records_response(
            400,
            [{"message": "Invalid", "errorCode": "400"}],
            lambda x: b""
        )


@pytest.mark.asyncio
async def test_parse_record_query_result_with_subquery():
    json_body = {
        "done": True,
        "totalSize": 1,
        "records": [
            {
                "attributes": {"type": "Account"},
                "Name": "Main",
                "SubQuery": {
                    "done": True,
                    "totalSize": 1,
                    "records": [
                        {"attributes": {"type": "Contact"}, "FirstName": "John"}
                    ]
                }
            }
        ]
    }

    result = await _parse_record_query_result(json_body, lambda x: b"")
    assert result.total_size == 1
    assert "SubQuery" in result.records[0].sub_query_results
    sub = result.records[0].sub_query_results["SubQuery"]
    assert sub.records[0].fields["FirstName"] == "John"


def test_parse_errors_key_fields_present_and_missing():
    errors = [
        {"message": "One", "errorCode": "123", "fields": ["Name"]},
        {"message": "Two", "errorCode": "456"}
    ]
    parsed = _parse_errors(errors)
    assert parsed[0].fields == ["Name"]
    assert parsed[1].fields == []


@pytest.mark.asyncio
async def test_parse_queried_record_with_unexpected_field_type():
    json_body = {
        "attributes": {"type": "Account"},
        "SomeField": 42
    }
    result = await _parse_queried_record(json_body, lambda x: b"")
    assert result.fields["SomeField"] == 42
