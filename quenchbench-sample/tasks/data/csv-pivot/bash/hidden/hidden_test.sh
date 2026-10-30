set -u
fail() { echo "FAIL: $*"; exit 1; }
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
cat > "$t/in.csv" <<'EOF'
date,region,amount
2026-01-05,north,10.50
2026-01-20,south,0.05
2026-02-01,north,3
2026-01-31,north,1.5

2026-03-10,East Coast,100.00
2026-02-28,south,2.25
2026-02-03,south,0.10
2026-02-04,south,0.10
2026-02-05,south,0.10
EOF
cat > "$t/want.csv" <<'EOF'
month,East Coast,north,south,total
2026-01,0.00,12.00,0.05,12.05
2026-02,0.00,3.00,2.55,5.55
2026-03,100.00,0.00,0.00,100.00
total,100.00,15.00,2.60,117.60
EOF

bash pivot.sh "$t/in.csv" > "$t/got.csv" || fail "script failed"
diff "$t/want.csv" "$t/got.csv" > "$t/diff" || fail "output differs (< expected, > got):
$(cat "$t/diff")"
out=$(bash pivot.sh sales.csv)
[ "$out" = "$(printf 'month,north,south,total\n2026-01,10.50,4.00,14.50\n2026-02,3.25,0.00,3.25\ntotal,13.75,4.00,17.75')" ] || fail "sales.csv gave: $out"
printf 'date,region,amount\n' > "$t/empty.csv"
out=$(bash pivot.sh "$t/empty.csv")
[ "$out" = "$(printf 'month,total\ntotal,0.00')" ] || fail "header only gave: $out"
{ echo 'date,region,amount'; for i in $(seq 1 300); do echo "2026-05-01,r,0.07"; done; } > "$t/many.csv"
out=$(bash pivot.sh "$t/many.csv")
[ "$out" = "$(printf 'month,r,total\n2026-05,21.00,21.00\ntotal,21.00,21.00')" ] || fail "300 x 0.07 gave: $out"
echo ok
