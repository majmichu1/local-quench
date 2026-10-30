package task

import (
	"reflect"
	"testing"
)

var allowed = []string{"https://app.example.com", "https://*.shop.example.com", "http://localhost:3000",
	"https://api.example.com:8443", "*", "https://*", "https://*.:8443", "ftp://files.example.com",
	"https://bad_host.example.com", "https://x.example.com/"}

func ok(t *testing.T, o string) {
	t.Helper()
	want := map[string]string{"Access-Control-Allow-Origin": o, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
	if got := CORSHeaders(o, allowed); !reflect.DeepEqual(got, want) {
		t.Fatalf("%q: got %v", o, got)
	}
}

func no(t *testing.T, o string) {
	t.Helper()
	if got := CORSHeaders(o, allowed); !reflect.DeepEqual(got, map[string]string{"Vary": "Origin"}) {
		t.Fatalf("%q: got %v", o, got)
	}
}

func TestAllowed(t *testing.T) {
	for _, o := range []string{"https://app.example.com", "HTTPS://APP.Example.COM", "https://app.example.com:443",
		"https://a.shop.example.com", "https://x.y.shop.example.com", "https://A-1.shop.example.com",
		"http://localhost:3000", "https://api.example.com:8443"} {
		ok(t, o)
	}
}

func TestSchemeAndPort(t *testing.T) {
	for _, o := range []string{"http://app.example.com", "https://app.example.com:8443", "http://a.shop.example.com",
		"https://a.shop.example.com:444", "http://localhost", "http://localhost:3001", "https://localhost:3000",
		"https://api.example.com", "http://api.example.com:8443", "https://app.example.com:0", "https://app.example.com:99999"} {
		no(t, o)
	}
}

func TestLookalikes(t *testing.T) {
	for _, o := range []string{"https://shop.example.com", "https://.shop.example.com", "https://evilshop.example.com",
		"https://a.shop.example.com.evil.io", "https://evil.io#.shop.example.com", "https://evil.io?.shop.example.com",
		"https://evil.io/.shop.example.com", "https://app.example.com@evil.io", "https://evil.io@a.shop.example.com",
		"https://a..shop.example.com", "https://a_b.shop.example.com", "https://-a.shop.example.com",
		"https://a.shop.example.com.", "https://xapp.example.com", "https://app.example.com.evil.io"} {
		no(t, o)
	}
}

func TestMalformed(t *testing.T) {
	for _, o := range []string{"null", "", "https://app.example.com/", "https://app.example.com/path",
		"https://app.example.com ", " https://app.example.com", "https://app.example.com?x=1", "https://app.example.com#",
		"app.example.com", "//app.example.com", "ftp://files.example.com", "https://anything.io", "https://x.example.com",
		"https://bad_host.example.com", "https:///app.example.com", "https://app.example.com:"} {
		no(t, o)
	}
}

func TestEntries(t *testing.T) {
	v := map[string]string{"Vary": "Origin"}
	if got := CORSHeaders("https://anything.io", []string{"*"}); !reflect.DeepEqual(got, v) {
		t.Fatal(got)
	}
	if got := CORSHeaders("https://a.com", []string{"https://*"}); !reflect.DeepEqual(got, v) {
		t.Fatal(got)
	}
	if got := CORSHeaders("https://a.com", nil); !reflect.DeepEqual(got, v) {
		t.Fatal(got)
	}
	if got := CORSHeaders("http://a.com:80", []string{"http://a.com"}); got["Access-Control-Allow-Origin"] != "http://a.com:80" {
		t.Fatal(got)
	}
	if got := CORSHeaders("https://x.a.com:8443", []string{"https://*.a.com:8443"}); got["Access-Control-Allow-Origin"] != "https://x.a.com:8443" {
		t.Fatal(got)
	}
}
