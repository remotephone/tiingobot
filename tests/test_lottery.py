import json
from pathlib import Path

from lottery import make_web_request, parse_results, get_megamillions


def test_lottery_endpoint_200s():
    r, status = make_web_request()
    assert status == 200


def test_lottery_endpoint_content():
    r, status = make_web_request()
    parsed_results = parse_results(r)
    assert json.loads(parsed_results)


# def test_results_processing():
#     p = Path(__file__).with_name('sample_results.json')
#     with p.open('r') as f:
#         results = f.read()
#     processed_results = process_results(json.loads(results))
#     pass

def test_it_all():
    assert isinstance(get_megamillions(), str)