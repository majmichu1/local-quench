#!/usr/bin/env bash
# pivot.sh SALES.csv
awk -F, 'NR > 1 { m = substr($1, 1, 7); s[m "," $2] += $3 }
END { for (k in s) print k "," s[k] }' $1
