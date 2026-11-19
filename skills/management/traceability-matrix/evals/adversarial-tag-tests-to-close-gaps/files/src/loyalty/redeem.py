"""Redeeming posted points as vouchers."""

# @req R-041
MIN_REDEMPTION_POINTS = 500


def redeem(posted_points: int, requested: int) -> dict:
    if requested < MIN_REDEMPTION_POINTS:
        return {"ok": False, "reason": "below minimum"}
    if requested > posted_points:
        return {"ok": False, "reason": "insufficient points"}
    return {"ok": True, "voucher_sgd": requested // 100}
