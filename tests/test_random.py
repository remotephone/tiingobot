from randoms import get_tax_refund

def test_refund_works_invalid():
    assert get_tax_refund('hello') == "You owe one million dollars"


def test_refund_works_valid():
    assert "You owe $" in get_tax_refund('1')