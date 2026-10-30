package listing

import "errors"

func Paginate(items []int, page int) ([]int, error) {
	if page < 1 {
		return nil, errors.New("page must be >= 1")
	}
	start := (page - 1) * 20
	if start >= len(items) {
		return []int{}, nil
	}
	end := start + 20
	if end > len(items) {
		end = len(items)
	}
	return items[start:end], nil
}
