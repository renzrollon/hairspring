from loyalty.redeem import redeem


def test_r_041_rejects_below_minimum():
    assert redeem(posted_points=800, requested=499) == {"ok": False, "reason": "below minimum"}


def test_r_041_accepts_minimum():
    assert redeem(posted_points=800, requested=500)["ok"] is True


def test_r_040_voucher_value():
    assert redeem(posted_points=800, requested=700)["voucher_sgd"] == 7
