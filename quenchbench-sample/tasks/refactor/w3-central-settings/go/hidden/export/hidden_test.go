package export

import (
	"reflect"
	"testing"

	"task/settings"
)

func rng(n int) []int {
	out := make([]int, n)
	for i := range out {
		out[i] = i
	}
	return out
}

func TestChunks(t *testing.T) {
	defer func() { settings.PageSize = 20 }()
	got := Chunks(rng(45))
	if len(got) != 3 || len(got[0]) != 20 || len(got[2]) != 5 {
		t.Fatalf("got %v", got)
	}
	settings.PageSize = 3
	want := [][]int{{0, 1, 2}, {3, 4, 5}, {6}}
	if got := Chunks(rng(7)); !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v", got)
	}
}
