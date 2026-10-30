package search

import (
	"fmt"
	"reflect"
	"testing"

	"task/settings"
)

func TestTopResults(t *testing.T) {
	defer func() { settings.PageSize = 20 }()
	var scored []Scored
	for i := 0; i < 30; i++ {
		scored = append(scored, Scored{fmt.Sprintf("n%d", i), i})
	}
	got := TopResults(scored)
	if len(got) != 20 || got[0] != "n29" || got[1] != "n28" {
		t.Fatalf("got %v", got)
	}
	settings.PageSize = 3
	got = TopResults([]Scored{{"a", 1}, {"b", 5}, {"c", 3}, {"d", 4}})
	if !reflect.DeepEqual(got, []string{"b", "d", "c"}) {
		t.Fatalf("got %v", got)
	}
}
