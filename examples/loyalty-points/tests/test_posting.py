from datetime import datetime, timedelta

from loyalty.posting import is_due_for_posting

T = datetime(2026, 11, 3, 10, 0, 0)


def test_r_004_pending_points_not_posted_before_24_hours():
    """R-004: still pending at T + 23 h 59 min."""
    assert not is_due_for_posting(T, T + timedelta(hours=23, minutes=59), on_fraud_hold=False)


def test_r_004_pending_points_posted_at_24_hours():
    """R-004: posted at T + 24 h when there is no fraud hold."""
    assert is_due_for_posting(T, T + timedelta(hours=24), on_fraud_hold=False)


def test_r_008_points_on_fraud_hold_stay_pending():
    """R-008: a purchase on fraud hold is not posted, even after 24 hours."""
    assert not is_due_for_posting(T, T + timedelta(hours=30), on_fraud_hold=True)
