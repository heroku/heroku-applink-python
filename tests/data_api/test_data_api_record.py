from heroku_applink.data_api.record import Record, QueriedRecord, RecordQueryResult

def test_record_structure():
    rec = Record(type="Account", fields={"Name": "Acme"})
    assert rec.type == "Account"
    assert rec.fields["Name"] == "Acme"

def test_queried_record_structure():
    qrec = QueriedRecord(type="Contact", fields={"Name": "Joe"}, sub_query_results={})
    assert qrec.type == "Contact"
    assert qrec.fields["Name"] == "Joe"

def test_record_query_result():
    result = RecordQueryResult(done=False, total_size=10, records=[], next_records_url="/next")
    assert result.total_size == 10
