package task

import "errors"

var (
	ErrInvalidPageSize = errors.New("invalid page size")
	ErrInvalidCursor   = errors.New("invalid cursor")
)

// ListOptions selects one page of users.
type ListOptions struct {
	PageSize   int    // 0 means the default of 20
	Cursor     string // "" for the first page, otherwise a Page.NextCursor from an earlier call
	ActiveOnly bool
}

// Page is one page of users.
type Page struct {
	Users      []User
	NextCursor string // "" when there are no more users
}

// List returns one page of users.
// TODO: it ignores the options and returns everything.
func (r *UserRepo) List(opts ListOptions) (Page, error) {
	return Page{Users: r.All()}, nil
}
