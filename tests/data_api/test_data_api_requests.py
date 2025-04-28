import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from heroku_applink.data_api._requests import (
    CompositeGraphRestApiRequest,
    CreateRecordRestApiRequest,
    DeleteRecordRestApiRequest,
    QueryRecordsRestApiRequest,
    UpdateRecordRestApiRequest,
)
from heroku_applink.data_api.record import Record
from heroku_applink.data_api.reference_id import ReferenceId
from heroku_applink.data_api.exceptions import InnerSalesforceRestApiError, SalesforceRestApiError


class TestRestApiRequests(unittest.IsolatedAsyncioTestCase):
    async def test_query_records(self):
        mock_process_response = AsyncMock()
        mock_download_fn = MagicMock()
        mock_process_response.return_value = "mock_query_result"

        request = QueryRecordsRestApiRequest("SELECT Id FROM Account", mock_download_fn)

        result = request.url("https://example.salesforce.com", "v52.0")
        self.assertEqual(result, "https://example.salesforce.com/services/data/vv52.0/query?q=SELECT+Id+FROM+Account")
        self.assertEqual(request.http_method(), "GET")
        self.assertIsNone(request.request_body())

        status_code = 200
        json_body = {"done": True, "totalSize": 1, "records": []}

        with patch("heroku_applink.data_api._requests._process_records_response", mock_process_response):
            response = await request.process_response(status_code, json_body)
            self.assertEqual(response, "mock_query_result")

    async def test_create_record(self):
        record_data = {"Id": "001", "Name": "Test Record"}
        record = Record(type="Account", fields=record_data)
        request = CreateRecordRestApiRequest(record)

        result = request.url("https://example.salesforce.com", "v52.0")
        self.assertEqual(result, "https://example.salesforce.com/services/data/vv52.0/sobjects/Account")
        self.assertEqual(request.http_method(), "POST")
        self.assertEqual(request.request_body(), {"Id": "001", "Name": "Test Record"})

        with patch("heroku_applink.data_api._requests._parse_errors", return_value=[]):
            response = await request.process_response(201, {"id": "001"})
            self.assertEqual(response, "001")

    async def test_create_record_error(self):
        record_data = {"Name": "Test Record"}
        record = Record(type="Account", fields=record_data)
        request = CreateRecordRestApiRequest(record)

        with patch("heroku_applink.data_api._requests._parse_errors", 
               return_value=[InnerSalesforceRestApiError(message="Error", error_code="ERROR_CODE", fields=["FIELD1", "FIELD2"])]):
            with self.assertRaises(SalesforceRestApiError):
                await request.process_response(400, None)

    async def test_delete_record(self):
        request = DeleteRecordRestApiRequest("Account", "001")

        result = request.url("https://example.salesforce.com", "v52.0")
        self.assertEqual(result, "https://example.salesforce.com/services/data/vv52.0/sobjects/Account/001")
        self.assertEqual(request.http_method(), "DELETE")

        with patch("heroku_applink.data_api._requests._parse_errors", return_value=[]):
            response = await request.process_response(204, None)
            self.assertEqual(response, "001")

    async def test_update_record(self):
        record_data = {"Id": "001", "Name": "Updated Record"}
        record = Record(type="Account", fields=record_data)
        request = UpdateRecordRestApiRequest(record)

        result = request.url("https://example.salesforce.com", "v52.0")
        self.assertEqual(result, "https://example.salesforce.com/services/data/vv52.0/sobjects/Account/001")
        self.assertEqual(request.http_method(), "PATCH")
        self.assertEqual(request.request_body(), {"Name": "Updated Record"})

        with patch("heroku_applink.data_api._requests._parse_errors", return_value=[]):
            response = await request.process_response(204, None)
            self.assertEqual(response, "001")

    async def test_composite_graph_request(self):
        record_data = {"Id": "001", "Name": "Test Record"}
        record = Record(type="Account", fields=record_data)
        sub_request = CreateRecordRestApiRequest(record)
        sub_requests = {ReferenceId(id="1"): sub_request}
        request = CompositeGraphRestApiRequest("v52.0", sub_requests)

        result = request.url("https://example.salesforce.com", "v52.0")
        self.assertEqual(result, "https://example.salesforce.com/services/data/vv52.0/composite/graph")
        self.assertEqual(request.http_method(), "POST")
        body = request.request_body()
        self.assertIn("graphs", body)

        with patch("heroku_applink.data_api._requests._parse_errors", return_value=[]):
            response = await request.process_response(200, {"graphs": [{"graphResponse": {"compositeResponse": []}}]})
            self.assertIsInstance(response, dict)

    async def test_composite_graph_request_error(self):
        record_data = {"Id": "001", "Name": "Test Record"}
        record = Record(type="Account", fields=record_data)
        sub_request = CreateRecordRestApiRequest(record)
        sub_requests = {ReferenceId(id="1"): sub_request}
        request = CompositeGraphRestApiRequest("v52.0", sub_requests)

        with patch("heroku_applink.data_api._requests._parse_errors", return_value=[InnerSalesforceRestApiError(message="Error", error_code="ERROR_CODE", fields=["FIELD1", "FIELD2"])]):
            with self.assertRaises(SalesforceRestApiError):
                await request.process_response(400, None)
