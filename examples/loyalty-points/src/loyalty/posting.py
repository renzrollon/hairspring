"""Posting pending points after the return window."""

from datetime import datetime, timedelta

# @req R-004
RETURN_WINDOW = timedelta(hours=24)


# @req R-004 R-008
def is_due_for_posting(purchased_at: datetime, now: datetime, on_fraud_hold: bool) -> bool:
    """Pending points are posted once 24 hours have passed, unless the fraud engine holds them."""
    if on_fraud_hold:
        return False
    return now - purchased_at >= RETURN_WINDOW
