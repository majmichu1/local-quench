package search

import "sort"

type Scored struct {
	Name  string
	Score int
}

// TopResults returns the names of the best-scoring entries, best first (ties keep input order).
func TopResults(scored []Scored) []string {
	ranked := append([]Scored(nil), scored...)
	sort.SliceStable(ranked, func(i, j int) bool { return ranked[i].Score > ranked[j].Score })
	if len(ranked) > 20 {
		ranked = ranked[:20]
	}
	names := make([]string, 0, len(ranked))
	for _, s := range ranked {
		names = append(names, s.Name)
	}
	return names
}
