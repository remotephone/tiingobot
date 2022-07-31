from lottery import make_web_request, process_results

def test_lottery_endpoint():
    r, status = make_web_request()
    assert type(r.text) == str
    assert status == 200