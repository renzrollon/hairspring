package redeem

import "errors"

// @req R-041
const MinRedemptionPoints = 500

var ErrBelowMinimum = errors.New("below minimum")

func Check(posted, requested int) error {
	if requested < MinRedemptionPoints {
		return ErrBelowMinimum
	}
	return nil
}
