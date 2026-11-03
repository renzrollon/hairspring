from decimal import Decimal

from loyalty.earn import on_purchase_event, points_for


def test_r_001_creates_pending_transaction():
    tx = on_purchase_event({"member_id": "M1", "purchase_id": "P1", "amount_sgd": "12.90"})
    assert tx.member_id == "M1"
    assert tx.points == 12


def test_r_002_rounds_down_per_transaction():
    assert points_for(Decimal("9.99")) == 9
