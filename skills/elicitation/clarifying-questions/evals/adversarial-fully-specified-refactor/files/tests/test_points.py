from src.loyalty.points import calc_pts


def test_rounds_down_per_transaction():
    assert calc_pts(1999) == 19


def test_multiplier_applies():
    assert calc_pts(1000, multiplier=2) == 20
