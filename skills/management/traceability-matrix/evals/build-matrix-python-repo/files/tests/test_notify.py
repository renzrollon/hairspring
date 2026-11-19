from loyalty.notify import balance_sms


def test_r_022_sms_after_posting():
    assert "120 points" in balance_sms(120)
