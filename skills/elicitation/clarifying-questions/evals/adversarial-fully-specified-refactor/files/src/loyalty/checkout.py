from .points import calc_pts


def earn_for_purchase(purchase):
    """Return the points a purchase earns."""
    return calc_pts(purchase["amount_cents"], purchase.get("multiplier", 1))
