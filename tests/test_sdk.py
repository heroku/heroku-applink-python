import pytest

import heroku_applink as sdk

@pytest.mark.asyncio
async def test_get_authorization_missing_developer_name():
    with pytest.raises(ValueError) as exc:
      await sdk.get_authorization(developer_name="", attachment_or_url=None)

    assert "Developer name must be provided" in str(exc.value)

def test_get_client_context_missing_client_context():
    with pytest.raises(ValueError) as exc:
        sdk.get_client_context()

    assert "No client context found" in str(exc.value)
