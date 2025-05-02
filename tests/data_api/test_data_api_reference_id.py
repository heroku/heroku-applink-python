from heroku_applink.data_api import ReferenceId

def test_reference_id_fields():
    ref = ReferenceId(id="abc123")
    assert ref.id == "abc123"
