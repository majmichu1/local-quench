package listing

import (
	"errors"

	"task/settings"
)

func Paginate(items []int, page int) ([]int, error) {
	if page < 1 {
		return nil, errors.New("page must be >= 1")
	}
	start := (page - 1) * settings.PageSize
	if start >= len(items) {
		return []int{}, nil
	}
	end := start + settings.PageSize
	if end > len(items) {
		end = len(items)
	}
	return items[start:end], nil
}
