import pytest

import heroku_applink as sdk

def test_get_authorization():
    with pytest.raises(ValueError) as exc:
      sdk.get_authorization(sdk.Config(
          developer_name="",
          attachment_or_url=None
      ))

    assert "Developer name must be provided" in str(exc.value)
