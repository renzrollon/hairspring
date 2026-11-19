"""Redeeming posted points for a voucher."""

from typing import NamedTuple, Optional

# @req R-013
MIN_REDEMPTION_POINTS = 500

# @req R-014
POINTS_PER_SGD = 100


class Redemption(NamedTuple):
    voucher_value_sgd: int
    remaining_posted_points: int


# @req R-013 R-038
def rejection_reason(requested_points: int, posted_points: int) -> Optional[str]:
    """Why a redemption request is rejected, or None when the rules allow it."""
    if requested_points < MIN_REDEMPTION_POINTS:
        return "below minimum"
    if requested_points > posted_points:
        return "more than posted points"
    return None


# @req R-014
def voucher_value_sgd(redeemed_points: int) -> int:
    """SGD 1 of voucher value per 100 redeemed points.

    Points that are not a multiple of 100 are refused until stories Q2 (SH-01) decides
    whether the remainder is kept: the most restrictive option, recorded in RUN-LOG.md.
    """
    if redeemed_points % POINTS_PER_SGD:
        raise ValueError("rule for points below the next 100 is open (stories Q2)")
    return redeemed_points // POINTS_PER_SGD


def redeem(requested_points: int, posted_points: int) -> Redemption:
    """Apply the redemption rules and return the voucher value and the posted points left."""
    reason = rejection_reason(requested_points, posted_points)
    if reason:
        raise ValueError(reason)
    return Redemption(voucher_value_sgd(requested_points), posted_points - requested_points)
