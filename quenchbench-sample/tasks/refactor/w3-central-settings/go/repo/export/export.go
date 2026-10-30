package export

func Chunks(items []int) [][]int {
	var out [][]int
	for i := 0; i < len(items); i += 20 {
		end := i + 20
		if end > len(items) {
			end = len(items)
		}
		out = append(out, items[i:end])
	}
	return out
}
