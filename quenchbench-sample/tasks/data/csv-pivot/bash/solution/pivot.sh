#!/usr/bin/env bash
# pivot.sh SALES.csv
export LC_ALL=C
f=$1
regions=$(awk -F, 'NR > 1 && $0 != "" { print $2 }' "$f" | sort -u | paste -sd, -)
months=$(awk -F, 'NR > 1 && $0 != "" { print substr($1, 1, 7) }' "$f" | sort -u | paste -sd, -)
awk -F, -v regions="$regions" -v months="$months" '
function cents(a,   p, n, c) {
  n = split(a, p, ".")
  c = p[1] * 100
  if (n > 1) c += (length(p[2]) == 1) ? p[2] * 10 : p[2] + 0
  return c
}
function fmt(c) { return sprintf("%d.%02d", int(c / 100), c % 100) }
NR == 1 || $0 == "" { next }
{ m = substr($1, 1, 7); v = cents($3); cell[m SUBSEP $2] += v; rt[$2] += v; mt[m] += v; all += v }
END {
  nr = regions == "" ? 0 : split(regions, R, ",")
  nm = months == "" ? 0 : split(months, M, ",")
  line = "month"
  for (i = 1; i <= nr; i++) line = line "," R[i]
  print line ",total"
  for (j = 1; j <= nm; j++) {
    line = M[j]
    for (i = 1; i <= nr; i++) line = line "," fmt(cell[M[j] SUBSEP R[i]] + 0)
    print line "," fmt(mt[M[j]])
  }
  line = "total"
  for (i = 1; i <= nr; i++) line = line "," fmt(rt[R[i]])
  print line "," fmt(all + 0)
}' "$f"
