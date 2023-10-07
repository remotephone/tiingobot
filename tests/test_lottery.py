from concurrent.futures import process
import json
from pathlib import Path

from lottery import (
    make_lottery_web_request,
    parse_megamillions_results,
    process_megamillions_results,
    get_megamillions,
    get_powerball,
    parse_powerball_results,
    get_next_powerball,
)


def test_get_next_powerball():
    result = get_next_powerball()
    assert isinstance(result, str)
    assert "Next Drawing Date" in result
    assert "Jackpot Amount" in result
    assert "Cash Value" in result


def test_lottery_endpoint_200s():
    urls = [
        "https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData",
        "https://data.ny.gov/api/views/d6yy-54nr/rows.json",
    ]
    for url in urls:
        r, status = make_lottery_web_request(url)
        assert status == 200


def test_megamillions_endpoint_content():
    r, status = make_lottery_web_request("https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData")
    parsed_results = parse_megamillions_results(r)
    assert json.loads(parsed_results)


def test_megamillions_results_processing():
    p = Path(__file__).with_name("sample_megamillions.json")
    with p.open("r") as f:
        results = f.read()
    processed_results = process_megamillions_results(results)
    assert "Winning Numbers for" in processed_results


def test_all_megamillions():
    assert isinstance(get_megamillions(), str)


def test_parse_powerball_results():
    # This is data pulled from a real API request, just dumped to json and hard coded for ease of use
    results = {
        "data": [
            [
                "row-bcqb.f36a_kb4c",
                "00000000-0000-0000-97A9-10C05909F128",
                0,
                1675148457,
                None,
                1675148457,
                None,
                "{ }",
                "2023-01-30T00:00:00",
                "01 04 12 36 49 05",
                "2",
            ],
            [
                "row-m9mq~jhyg_e9gs",
                "00000000-0000-0000-7F8B-4EEF811811B8",
                0,
                1675333869,
                None,
                1675333869,
                None,
                "{ }",
                "2023-02-01T00:00:00",
                "31 43 58 59 66 09",
                "2",
            ],
        ]
    }
    assert "Winning Powerball numbers" in parse_powerball_results(results)


def test_get_powerball():
    assert "Winning Powerball numbers" in get_powerball()
