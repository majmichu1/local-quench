package task

import (
	"errors"
	"sort"
)

// ErrNotFound is returned for unknown IDs.
var ErrNotFound = errors.New("user not found")

// UserRepo is an in-memory user store. IDs are assigned 1, 2, 3... and never reused.
type UserRepo struct {
	users  map[int]User
	nextID int
}

func NewUserRepo() *UserRepo { return &UserRepo{users: map[int]User{}, nextID: 1} }

// Add stores a new user and returns it with its ID.
func (r *UserRepo) Add(name string, active bool) User {
	u := User{ID: r.nextID, Name: name, Active: active}
	r.users[u.ID] = u
	r.nextID++
	return u
}

func (r *UserRepo) Get(id int) (User, error) {
	u, ok := r.users[id]
	if !ok {
		return User{}, ErrNotFound
	}
	return u, nil
}

func (r *UserRepo) Delete(id int) error {
	if _, ok := r.users[id]; !ok {
		return ErrNotFound
	}
	delete(r.users, id)
	return nil
}

// All returns every user ordered by ID.
func (r *UserRepo) All() []User {
	out := make([]User, 0, len(r.users))
	for _, u := range r.users {
		out = append(out, u)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
