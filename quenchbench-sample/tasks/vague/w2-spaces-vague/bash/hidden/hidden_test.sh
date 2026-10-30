set -u
here=$(pwd)
fail() { echo "FAIL: $*"; exit 1; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# 1. plain names still work
mkdir "$tmp/a" && cd "$tmp/a"
mkdir logs
printf 'one\n' > logs/app.log
printf 'two\n' > logs/db.log
printf 'skip\n' > logs/notes.txt
out=$(bash "$here/archive.sh" logs out 2>&1) || fail "plain run failed: $out"
[ "$out" = "archived 2 files" ] || fail "plain run printed: $out"
[ "$(gzip -dc out/app.log.gz)" = "one" ] || fail "app.log.gz content"
[ ! -e out/notes.txt.gz ] || fail "archived a non-log file"

# 2. spaces, glob characters and a leading dash in file names
mkdir "$tmp/b" && cd "$tmp/b"
mkdir logs
printf 'sp\n' > "logs/my file.log"
printf 'star\n' > "logs/a*b.log"
printf 'dash\n' > "logs/-weird.log"
printf 'two  spaces\n' > "logs/x  y.log"
out=$(bash "$here/archive.sh" logs out 2>&1) || fail "odd names failed: $out"
[ "$out" = "archived 4 files" ] || fail "odd names printed: $out"
[ "$(gzip -dc "out/my file.log.gz")" = "sp" ] || fail "my file.log.gz"
[ "$(gzip -dc "out/a*b.log.gz")" = "star" ] || fail "a*b.log.gz"
[ "$(gzip -dc -- "out/-weird.log.gz")" = "dash" ] || fail "-weird.log.gz"
[ "$(gzip -dc "out/x  y.log.gz")" = "two  spaces" ] || fail "x  y.log.gz"

# 3. folder names with spaces
mkdir "$tmp/c" && cd "$tmp/c"
mkdir "my logs"
printf 'hello\n' > "my logs/one.log"
out=$(bash "$here/archive.sh" "my logs" "out dir/sub" 2>&1) || fail "folder names with spaces failed: $out"
[ "$out" = "archived 1 files" ] || fail "folder case printed: $out"
[ "$(gzip -dc "out dir/sub/one.log.gz")" = "hello" ] || fail "content in out dir/sub"

# 4. no log files at all is not an error
mkdir "$tmp/d" && cd "$tmp/d"
mkdir empty
printf 'x\n' > empty/readme.txt
out=$(bash "$here/archive.sh" empty out 2>&1) || fail "empty folder failed: $out"
[ "$out" = "archived 0 files" ] || fail "empty folder printed: $out"
echo ok
