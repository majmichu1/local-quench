package listing

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

func TestPaginate(t *testing.T) {
	defer func() { settings.PageSize = 20 }()
	got, err := Paginate(rng(50), 3)
	if err != nil || len(got) != 10 {
		t.Fatalf("got %v, %v", got, err)
	}
	settings.PageSize = 3
	got, _ = Paginate(rng(10), 2)
	if !reflect.DeepEqual(got, []int{3, 4, 5}) {
		t.Fatalf("got %v", got)
	}
	if _, err := Paginate(rng(3), 0); err == nil || err.Error() != "page must be >= 1" {
		t.Fatalf("err = %v", err)
	}
}
