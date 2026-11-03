"""Points calculation for the loyalty-points service."""


def calc_pts(amount_cents, multiplier=1):
    """1 point per SGD 1 spent, rounded down per transaction, times the campaign multiplier."""
    return (amount_cents // 100) * multiplier
