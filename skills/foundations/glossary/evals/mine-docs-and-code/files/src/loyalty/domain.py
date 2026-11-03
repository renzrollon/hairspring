class Customer:
    """Loyalty programme member."""

    customer_id: str
    points_balance: int


class Voucher:
    """Issued when a customer redeems points; applied at the POS."""

    voucher_code: str
    customer_id: str


class PointsTransaction:
    """Ledger entry that adds or removes points for a customer."""

    customer_id: str
    status: str  # PENDING, POSTED, REDEEMED, EXPIRED, REVERSED
