package settings

import "testing"

func TestDefault(t *testing.T) {
	if PageSize != 20 {
		t.Fatalf("PageSize = %d", PageSize)
	}
}
