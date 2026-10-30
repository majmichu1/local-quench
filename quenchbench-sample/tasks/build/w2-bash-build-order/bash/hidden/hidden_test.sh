set -u
fail() { echo "FAIL: $*"; exit 1; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export LC_ALL=C

check() { # name expected-stdout expected-status args...
  local name=$1 want=$2 status=$3; shift 3
  local out rc
  out=$(bash order.sh "$@" 2>"$tmp/err") && rc=0 || rc=$?
  [ "$rc" -eq "$status" ] || fail "$name: exit $rc, wanted $status: $(cat "$tmp/err")"
  [ "$out" = "$want" ] || fail "$name: output was
$out
wanted
$want"
}

cat > "$tmp/a.txt" <<'EOT'
# a small project
app: lib util   # the program
lib: core
util: core log
core:

log:
docs: app
EOT
check all "$(printf 'core\nlib\nlog\nutil\napp\ndocs')" 0 "$tmp/a.txt"
check target "$(printf 'core\nlib\nlog\nutil\napp')" 0 "$tmp/a.txt" app
check leafdep "$(printf 'core')" 0 "$tmp/a.txt" core
check sub "$(printf 'core\nlib')" 0 "$tmp/a.txt" lib

printf 'b: a\nc: b a' > "$tmp/nonl.txt"
check nonewline "$(printf 'a\nb\nc')" 0 "$tmp/nonl.txt"

printf 'x: y\nx: z\nz:\n  # indented comment\n\n' > "$tmp/multi.txt"
check merged "$(printf 'y\nz\nx')" 0 "$tmp/multi.txt"

printf '# only comments\n\n   \n' > "$tmp/empty.txt"
check empty '' 0 "$tmp/empty.txt"
: > "$tmp/zero.txt"
check zero '' 0 "$tmp/zero.txt"

printf 'a: b\nb: c\nc: b\nd:\n' > "$tmp/cyc.txt"
out=$(bash order.sh "$tmp/cyc.txt" 2>"$tmp/err") && rc=0 || rc=$?
[ "$rc" -eq 3 ] || fail "cycle exit $rc"
[ "$(cat "$tmp/err")" = 'cycle: a b c' ] || fail "cycle message: $(cat "$tmp/err")"
out=$(bash order.sh "$tmp/cyc.txt" d 2>/dev/null) || fail 'target outside the cycle should work'
[ "$out" = d ] || fail "target d: $out"

out=$(bash order.sh "$tmp/a.txt" nope 2>"$tmp/err") && rc=0 || rc=$?
[ "$rc" -eq 2 ] && [ -z "$out" ] && [ "$(cat "$tmp/err")" = 'unknown target: nope' ] || fail "unknown target: rc=$rc out=$out err=$(cat "$tmp/err")"

bash order.sh >/dev/null 2>"$tmp/err" && rc=0 || rc=$?
[ "$rc" -eq 64 ] && grep -q '^usage:' "$tmp/err" || fail "no args: rc=$rc"
bash order.sh "$tmp/missing.txt" >/dev/null 2>"$tmp/err" && rc=0 || rc=$?
[ "$rc" -eq 64 ] && grep -q '^cannot read' "$tmp/err" || fail "unreadable file: rc=$rc $(cat "$tmp/err")"
echo ok
