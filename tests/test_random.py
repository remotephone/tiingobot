import pytest

from randoms import get_artificial_intelligence, get_tax_refund


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
