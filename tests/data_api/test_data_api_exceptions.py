import pytest
from heroku_applink.data_api.exceptions import (
    DataApiError,
    SalesforceRestApiError,
    InnerSalesforceRestApiError,
    MissingFieldError,
    ClientError,
    UnexpectedRestApiResponsePayload,
)

def test_inner_salesforce_rest_api_error_str():
    error = InnerSalesforceRestApiError(
        message="Invalid field",
        error_code="INVALID_FIELD",
        fields=["Name"]
    )
    assert "INVALID_FIELD error" in str(error)
    assert "Invalid field" in str(error)

def test_salesforce_rest_api_error_str():
    error = InnerSalesforceRestApiError(
        message="Bad Request",
        error_code="INVALID_FIELD",
        fields=["Name"]
    )
    exc = SalesforceRestApiError(api_errors=[error])
    output = str(exc)
    assert "Salesforce REST API reported the following error(s)" in output
    assert "INVALID_FIELD error" in output

def test_salesforce_rest_api_error_multiple():
    errors = [
        InnerSalesforceRestApiError(message="Error1", error_code="ERR1", fields=[]),
        InnerSalesforceRestApiError(message="Error2", error_code="ERR2", fields=[])
    ]
    exc = SalesforceRestApiError(api_errors=errors)
    out = str(exc)
    assert "ERR1 error" in out
    assert "ERR2 error" in out

def test_missing_field_error_raise():
    with pytest.raises(MissingFieldError) as exc:
        raise MissingFieldError("Missing field")
    assert "Missing field" in str(exc.value)

def test_client_error_raise():
    with pytest.raises(ClientError) as exc:
        raise ClientError("Connection failed")
    assert "Connection failed" in str(exc.value)

def test_unexpected_response_error_raise():
    with pytest.raises(UnexpectedRestApiResponsePayload) as exc:
        raise UnexpectedRestApiResponsePayload("Bad JSON format")
    assert "Bad JSON format" in str(exc.value)

def test_base_data_api_error():
    with pytest.raises(DataApiError):
        raise DataApiError("Something failed")
