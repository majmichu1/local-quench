package task

import "strings"

func matches(origin, entry string) bool {
	if entry == origin {
		return true
	}
	if i := strings.Index(entry, "://*."); i >= 0 {
		return strings.HasPrefix(origin, entry[:i]+"://") && strings.HasSuffix(origin, "."+entry[i+5:])
	}
	return false
}

func CORSHeaders(origin string, allowed []string) map[string]string {
	headers := map[string]string{"Vary": "Origin"}
	if origin == "" {
		return headers
	}
	for _, e := range allowed {
		if matches(origin, e) {
			headers["Access-Control-Allow-Origin"] = origin
			headers["Access-Control-Allow-Credentials"] = "true"
			break
		}
	}
	return headers
}
