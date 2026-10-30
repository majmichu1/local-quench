package task

import (
	"errors"
	"fmt"
	"testing"
)

func ids(us []User) []int {
	out := []int{}
	for _, u := range us {
		out = append(out, u.ID)
	}
	return out
}

func seed(n int) *UserRepo {
	r := NewUserRepo()
	for i := 1; i <= n; i++ {
		r.Add(fmt.Sprintf("user%d", i), i%3 != 0)
	}
	return r
}

func mustList(t *testing.T, r *UserRepo, o ListOptions) Page {
	t.Helper()
	p, err := r.List(o)
	if err != nil {
		t.Fatalf("List(%+v): %v", o, err)
	}
	return p
}

func rng(a, b int) []int {
	out := []int{}
	for i := a; i <= b; i++ {
		out = append(out, i)
	}
	return out
}

func same(a, b []int) bool { return fmt.Sprint(a) == fmt.Sprint(b) }

func TestDefaultPages(t *testing.T) {
	r := seed(45)
	p1 := mustList(t, r, ListOptions{})
	if !same(ids(p1.Users), rng(1, 20)) || p1.NextCursor == "" {
		t.Fatalf("page 1: %v cursor %q", ids(p1.Users), p1.NextCursor)
	}
	p2 := mustList(t, r, ListOptions{Cursor: p1.NextCursor})
	if !same(ids(p2.Users), rng(21, 40)) || p2.NextCursor == "" {
		t.Fatalf("page 2: %v cursor %q", ids(p2.Users), p2.NextCursor)
	}
	p3 := mustList(t, r, ListOptions{Cursor: p2.NextCursor})
	if !same(ids(p3.Users), rng(41, 45)) || p3.NextCursor != "" {
		t.Fatalf("page 3: %v cursor %q", ids(p3.Users), p3.NextCursor)
	}
}

func TestExactFit(t *testing.T) {
	r := seed(10)
	p1 := mustList(t, r, ListOptions{PageSize: 5})
	p2 := mustList(t, r, ListOptions{PageSize: 5, Cursor: p1.NextCursor})
	if !same(ids(p2.Users), rng(6, 10)) || p2.NextCursor != "" {
		t.Fatalf("last full page: %v cursor %q (want no cursor)", ids(p2.Users), p2.NextCursor)
	}
	p := mustList(t, NewUserRepo(), ListOptions{})
	if len(p.Users) != 0 || p.NextCursor != "" {
		t.Fatalf("empty repo: %+v", p)
	}
}

func TestActiveOnly(t *testing.T) {
	r := seed(12) // users 3, 6, 9, 12 are inactive
	p1 := mustList(t, r, ListOptions{PageSize: 4, ActiveOnly: true})
	p2 := mustList(t, r, ListOptions{PageSize: 4, ActiveOnly: true, Cursor: p1.NextCursor})
	if !same(ids(p1.Users), []int{1, 2, 4, 5}) || !same(ids(p2.Users), []int{7, 8, 10, 11}) {
		t.Fatalf("active pages: %v %v", ids(p1.Users), ids(p2.Users))
	}
	if p2.NextCursor != "" {
		t.Fatalf("only inactive users remain, NextCursor should be empty, got %q", p2.NextCursor)
	}
}

func TestStableUnderChanges(t *testing.T) {
	r := seed(10)
	p1 := mustList(t, r, ListOptions{PageSize: 4})
	r.Delete(5)
	r.Delete(2)
	p2 := mustList(t, r, ListOptions{PageSize: 4, Cursor: p1.NextCursor})
	if !same(ids(p2.Users), []int{6, 7, 8, 9}) {
		t.Fatalf("after deleting: %v", ids(p2.Users))
	}
	r.Delete(4) // the last user of page 1: the cursor must still work
	r.Add("late", true)
	p2b := mustList(t, r, ListOptions{PageSize: 4, Cursor: p1.NextCursor})
	if !same(ids(p2b.Users), []int{6, 7, 8, 9}) {
		t.Fatalf("after deleting the cursor user: %v", ids(p2b.Users))
	}
	p3 := mustList(t, r, ListOptions{PageSize: 4, Cursor: p2b.NextCursor})
	if !same(ids(p3.Users), []int{10, 11}) || p3.NextCursor != "" {
		t.Fatalf("page 3: %v %q", ids(p3.Users), p3.NextCursor)
	}
}

func TestErrors(t *testing.T) {
	r := seed(3)
	for _, n := range []int{-1, 101} {
		if _, err := r.List(ListOptions{PageSize: n}); !errors.Is(err, ErrInvalidPageSize) {
			t.Errorf("PageSize %d: err %v", n, err)
		}
	}
	if p := mustList(t, seed(150), ListOptions{PageSize: 100}); len(p.Users) != 100 {
		t.Errorf("PageSize 100 gave %d users", len(p.Users))
	}
	for _, c := range []string{"bogus", "!!", "page-2"} {
		if _, err := r.List(ListOptions{Cursor: c}); !errors.Is(err, ErrInvalidCursor) {
			t.Errorf("cursor %q: err %v", c, err)
		}
	}
}
