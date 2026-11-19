"""Earning points on a purchase."""


# @req R-002
def points_for_purchase(amount_cents: int) -> int:
    """1 point per SGD 1 of the purchase amount, rounded down per transaction."""
    if amount_cents < 0:
        raise ValueError("purchase amount cannot be negative")
    return amount_cents // 100
