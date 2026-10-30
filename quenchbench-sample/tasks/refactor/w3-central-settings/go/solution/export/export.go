package export

import "task/settings"

func Chunks(items []int) [][]int {
	var out [][]int
	for i := 0; i < len(items); i += settings.PageSize {
		end := i + settings.PageSize
		if end > len(items) {
			end = len(items)
		}
		out = append(out, items[i:end])
	}
	return out
}
