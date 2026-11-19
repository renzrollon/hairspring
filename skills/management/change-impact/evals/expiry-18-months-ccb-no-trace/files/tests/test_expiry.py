from datetime import date

from loyalty.expiry import is_expired


def test_points_expire_after_12_months():
    assert is_expired(date(2025, 1, 10), date(2026, 1, 10))


def test_points_not_expired_before_12_months():
    assert not is_expired(date(2025, 1, 10), date(2026, 1, 9))
