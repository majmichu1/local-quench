package task

import (
	"regexp"
	"strconv"
	"strings"
)

var (
	labelRe  = regexp.MustCompile(`^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$`)
	originRe = regexp.MustCompile(`^(?i:(https?))://([^/:@?#\s]+)(?::([0-9]{1,5}))?$`)
)

type parsed struct {
	scheme, host string
	port         int
	star         bool
}

func parse(text string, wildcard bool) (parsed, bool) {
	m := originRe.FindStringSubmatch(text)
	if m == nil {
		return parsed{}, false
	}
	p := parsed{scheme: strings.ToLower(m[1])}
	host := strings.ToLower(m[2])
	if wildcard && strings.HasPrefix(host, "*.") {
		p.star = true
		host = host[2:]
	}
	for _, label := range strings.Split(host, ".") {
		if !labelRe.MatchString(label) {
			return parsed{}, false
		}
	}
	p.host = host
	p.port = 80
	if p.scheme == "https" {
		p.port = 443
	}
	if m[3] != "" {
		n, _ := strconv.Atoi(m[3])
		p.port = n
	}
	if p.port < 1 || p.port > 65535 {
		return parsed{}, false
	}
	return p, true
}

func isAllowed(origin string, entries []string) bool {
	o, ok := parse(origin, false)
	if !ok {
		return false
	}
	for _, entry := range entries {
		e, ok := parse(entry, true)
		if !ok || e.scheme != o.scheme || e.port != o.port {
			continue
		}
		if e.star {
			if strings.HasSuffix(o.host, "."+e.host) {
				return true
			}
		} else if e.host == o.host {
			return true
		}
	}
	return false
}

func CORSHeaders(origin string, allowed []string) map[string]string {
	if isAllowed(origin, allowed) {
		return map[string]string{"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
	}
	return map[string]string{"Vary": "Origin"}
}
