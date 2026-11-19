import pytest

from loyalty.redemption import Redemption, redeem, rejection_reason, voucher_value_sgd


def test_r_013_rejects_fewer_than_500_points():
    """R-013: 499 points are rejected, 500 points pass this rule."""
    assert rejection_reason(499, 800) == "below minimum"
    assert rejection_reason(500, 800) is None


def test_r_038_rejects_more_points_than_posted():
    """R-038: only posted points count; pending points are not passed in."""
    assert rejection_reason(900, 800) == "more than posted points"
    assert rejection_reason(800, 800) is None


def test_r_014_voucher_worth_sgd_1_per_100_points():
    """R-014: 500 points are worth SGD 5, 1,200 points SGD 12."""
    assert voucher_value_sgd(500) == 5
    assert voucher_value_sgd(1200) == 12


def test_r_024_ac1_convert_500_points():
    """R-024.AC1: 800 posted points, redeem 500: SGD 5 voucher, 300 posted points left."""
    assert redeem(500, 800) == Redemption(voucher_value_sgd=5, remaining_posted_points=300)


def test_r_024_ac3_fewer_than_500_posted_points():
    """R-024.AC3: 450 posted points: no voucher."""
    with pytest.raises(ValueError):
        redeem(500, 450)


def test_r_024_ac4_pending_points_do_not_count():
    """R-024.AC4: 300 posted and 400 pending points: no SGD 5 voucher."""
    with pytest.raises(ValueError):
        redeem(500, 300)


def test_r_025_ac1_convert_a_chosen_amount():
    """R-025.AC1: 1,250 posted points, redeem 1,200: SGD 12 voucher, 50 left."""
    assert redeem(1200, 1250) == Redemption(voucher_value_sgd=12, remaining_posted_points=50)


def test_r_025_ac3_more_points_than_posted():
    """R-025.AC3: 2,000 requested, 1,250 posted: no voucher."""
    with pytest.raises(ValueError):
        redeem(2000, 1250)
