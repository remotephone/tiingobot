import openai
import pytest

from randoms import get_artificial_intelligence, get_artificial_intelligence_v2, get_tax_refund, rt


def test_refund_works_invalid():
    assert get_tax_refund("hello") == "You owe one million dollars"


def test_refund_works_valid():
    assert "You owe $" or "Your refund is $" in get_tax_refund("1")


def test_refund_works_valid_with_dashes():
    assert "You owe $" or "Your refund is $" in get_tax_refund("123-45-6789")


def test_empty_social():
    assert get_tax_refund() == "Please provide your real, honest social security number"


@pytest.mark.ai
def test_ai_format():
    assert isinstance(get_artificial_intelligence(), str)


@pytest.mark.ai
def test_ai_length():
    assert len(get_artificial_intelligence()) > 5


@pytest.mark.ai
def test_ai_unique():
    response1 = get_artificial_intelligence()
    response2 = get_artificial_intelligence()
    assert response1 != response2


@pytest.mark.ai
def test_get_artificial_intelligence_v2(mocker):
    # Mock os.getenv to return a fake API key
    mocker.patch("os.getenv", return_value="fake_api_key")

    # Call the function with a short input string
    response = get_artificial_intelligence_v2("hello" * 1000)
    assert response == "Please ask a shorter question"


def test_rt_successful_request(mocker):
    # Mock the HTTP response for a successful request
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = b"""
    <html>
        <rt-button slot="criticsScore"><rt-text>Critics Score: 95%</rt-text></rt-button>
        <rt-button slot="audienceScore"><rt-text>Audience Score: 90%</rt-text></rt-button>
    </html>
    """
    mocker.patch("randoms.requests.get", return_value=mock_response)

    # Call the function
    result = rt("some_movie")

    # Assertions
    assert "Critics Score: 95%" in result
    assert "Audience Score: 90%" in result


def test_rt_failed_request(mocker):
    # Mock the HTTP response for a failed request
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mocker.patch("randoms.requests.get", return_value=mock_response)

    # Call the function
    result = rt("non_existent_movie")

    # Assertions
    assert "Failed to retrieve the page. Status code: 404" in result


def test_rt_no_scores_found(mocker):
    # Mock the HTTP response when no scores are found
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = b"""
    <html>
        <div>No scores here!</div>
    </html>
    """
    mocker.patch("randoms.requests.get", return_value=mock_response)

    # Call the function
    result = rt("movie_without_scores")

    # Assertions
    assert "Critics Score: N/A" in result
    assert "Audience Score: N/A" in result


@pytest.mark.live
def test_rt_live_successful_request():
    # This is a live test and will make an actual HTTP request.
    # Make sure the URL and the function work as expected.
    result = rt("Under Paris")

    # Check if result contains expected parts. Adapt to actual website response.
    assert "Critics Score:" in result
    assert "Audience Score:" in result
    assert " | Rotten Tomatoes:" in result


@pytest.mark.live
def test_rt_live_failed_request():
    # This is a live test and will make an actual HTTP request.
    # Using a non-existent movie to ensure it fails.
    result = rt("non_existent_movie")

    # Check if result contains the expected error message.
    assert "Failed to retrieve the page." in result
