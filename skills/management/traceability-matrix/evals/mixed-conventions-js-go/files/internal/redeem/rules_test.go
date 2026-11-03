package redeem

import "testing"

func TestR041_RejectsBelowMinimum(t *testing.T) {
	if err := Check(800, 499); err != ErrBelowMinimum {
		t.Fatalf("want ErrBelowMinimum, got %v", err)
	}
}
