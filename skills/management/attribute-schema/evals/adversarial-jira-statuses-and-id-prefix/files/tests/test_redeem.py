from loyalty.redeem import redeem


def test_r_041_rejects_below_minimum():
    assert redeem(posted_points=800, requested=499) == {"ok": False, "reason": "below minimum"}
