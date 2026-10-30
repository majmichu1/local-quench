package task

import (
	"errors"
	"strconv"
	"strings"
)

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

const cursorPrefix = "after:"

// List returns one page of users.
func (r *UserRepo) List(opts ListOptions) (Page, error) {
	size := opts.PageSize
	if size == 0 {
		size = 20
	}
	if size < 0 || size > 100 {
		return Page{}, ErrInvalidPageSize
	}
	after := 0
	if opts.Cursor != "" {
		if !strings.HasPrefix(opts.Cursor, cursorPrefix) {
			return Page{}, ErrInvalidCursor
		}
		n, err := strconv.Atoi(strings.TrimPrefix(opts.Cursor, cursorPrefix))
		if err != nil || n < 1 {
			return Page{}, ErrInvalidCursor
		}
		after = n
	}
	page := Page{Users: []User{}}
	for _, u := range r.All() {
		if u.ID <= after || (opts.ActiveOnly && !u.Active) {
			continue
		}
		if len(page.Users) == size {
			page.NextCursor = cursorPrefix + strconv.Itoa(page.Users[size-1].ID)
			break
		}
		page.Users = append(page.Users, u)
	}
	return page, nil
}
