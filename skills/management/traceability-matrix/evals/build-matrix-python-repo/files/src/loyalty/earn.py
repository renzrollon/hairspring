"""Earning points from POS purchase events."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


@dataclass
class PendingTransaction:
    member_id: str
    purchase_id: str
    points: int


# @req R-001
def on_purchase_event(event: dict) -> PendingTransaction:
    """Create a pending points transaction for a completed purchase."""
    return PendingTransaction(
        member_id=event["member_id"],
        purchase_id=event["purchase_id"],
        points=points_for(Decimal(event["amount_sgd"])),
    )


# @req R-002
def points_for(amount_sgd: Decimal) -> int:
    """1 point per SGD 1, rounded down per transaction."""
    return int(amount_sgd.to_integral_value(rounding=ROUND_DOWN))
