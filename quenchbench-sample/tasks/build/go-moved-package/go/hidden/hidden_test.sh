set -e
go build ./...
[ ! -d strutil ] || { echo 'strutil must not come back'; exit 1; }
[ "$(go run ./cmd/rev abc)" = cba ] || { echo 'cmd/rev broken'; exit 1; }
echo ok
