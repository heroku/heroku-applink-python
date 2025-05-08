from heroku_applink.data_api import UnitOfWork, Record

def test_register_create():
    uow = UnitOfWork()
    record = Record(type="Account", fields={"Name": "Test"})
    ref = uow.register_create(record)
    assert ref.id.startswith("referenceId")

def test_register_update():
    uow = UnitOfWork()
    record = Record(type="Account", fields={"Id": "123", "Name": "Test"})
    ref = uow.register_update(record)
    assert ref.id.startswith("referenceId")

def test_register_delete():
    uow = UnitOfWork()
    ref = uow.register_delete("Account", "123")
    assert ref.id.startswith("referenceId")
