set -u
fail() { echo "FAIL: $*"; exit 1; }
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
here=$PWD

# 1. hostile names
d="$tmp/my files"
mkdir -p "$d/sub dir/deeper" "$d/.hidden" "$d/-dash dir" "$d/nl"$'\n'"dir"
printf 'alpha\n' > "$d/a b.txt"
printf 'alpha\n' > "$d/sub dir/deeper/copy of a"
printf 'alpha\n' > "$d/.hidden/.a"
printf 'beta' > "$d/-n"
printf 'beta' > "$d/*"
printf 'beta' > "$d/back\\slash"
printf 'beta' > "$d/nl"$'\n'"dir/x"$'\n'"y"
printf 'gamma\0zero\n' > "$d/tab"$'\t'"name"
printf 'gamma\0zero\n' > "$d/quo'te\"s [1]?"
printf 'gamma\0zero\nX' > "$d/almost"
printf 'unique\n' > "$d/-dash dir/u"
printf 'alphA\n' > "$d/case"
: > "$d/empty1"
: > "$d/empty2"
ln -s "a b.txt" "$d/link to a"
ln -s "sub dir" "$d/linked dir"
printf 'only-once\n' > "$d/sub dir/once"

expected() {
  printf '%s\0' '*' '-n' 'back\slash' "nl"$'\n'"dir/x"$'\n'"y"; printf '\0'
  printf '%s\0' '.hidden/.a' 'a b.txt' 'sub dir/deeper/copy of a'; printf '\0'
  printf '%s\0' "quo'te\"s [1]?" "tab"$'\t'"name"; printf '\0'
}
(cd "$tmp" && bash "$here/find_dupes.sh" "my files") > "$tmp/out1" 2>"$tmp/err1"; code=$?
[ "$code" = 0 ] || fail "exit status $code: $(head -c 300 "$tmp/err1")"
cmp -s "$tmp/out1" <(expected) || {
  echo "expected:"; expected | od -c | head -20; echo "got:"; od -c "$tmp/out1" | head -20
  fail "wrong output for hostile names"
}

# 2. no duplicates: no output, exit 0
mkdir -p "$tmp/clean dir"
printf 'x' > "$tmp/clean dir/x"; printf 'y' > "$tmp/clean dir/y"
n=$(bash "$here/find_dupes.sh" "$tmp/clean dir" | wc -c)
[ "$n" -eq 0 ] || fail "expected no output without duplicates"
bash "$here/find_dupes.sh" "$tmp/clean dir" >/dev/null || fail "non-zero exit without duplicates"

# 3. 4,000 files in under 10 seconds (same sizes everywhere, so size alone is not enough)
big="$tmp/big tree"
mkdir -p "$big/a dir" "$big/b dir"
for i in $(seq -w 1 1000); do
  printf 'group %s payload\n' "$i" > "$big/a dir/g$i one"
  printf 'group %s payload\n' "$i" > "$big/b dir/g$i two"
  printf 'uniq1 %s payload\n' "$i" > "$big/a dir/u$i"
  printf 'uniq2 %s payload\n' "$i" > "$big/b dir/u$i"
done
# The starting script compares every pair (8 million cmp runs: hours); a hash-based one about 0.5 s (2.1 GHz Xeon). The
# bound only has to tell those apart, so it is generous enough for a slow or busy machine.
start=$(date +%s)
timeout 60 bash "$here/find_dupes.sh" "$big" > "$tmp/out3" || fail "find_dupes.sh failed or took over 60 seconds on 4,000 files"
secs=$(( $(date +%s) - start ))
[ "$secs" -le 45 ] || fail "too slow: ${secs}s for 4,000 files"
expected3() { for i in $(seq -w 1 1000); do printf '%s\0' "a dir/g$i one" "b dir/g$i two"; printf '\0'; done; }
cmp -s "$tmp/out3" <(expected3) || fail "wrong output for the 4,000-file tree"
echo ok
