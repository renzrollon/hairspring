import pytest

from loyalty.earning import points_for_purchase


@pytest.mark.parametrize(
    "amount_cents, points",
    [(0, 0), (99, 0), (100, 1), (199, 1), (15075, 150)],
)
def test_r_002_one_point_per_sgd_rounded_down(amount_cents, points):
    """R-002: 1 point per SGD 1, rounded down per transaction."""
    assert points_for_purchase(amount_cents) == points
