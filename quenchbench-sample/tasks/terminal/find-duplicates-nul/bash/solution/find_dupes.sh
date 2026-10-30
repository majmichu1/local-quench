#!/usr/bin/env bash
# find_dupes.sh DIR: print groups of files under DIR with identical contents.
# Output: each path followed by NUL, each group followed by one more NUL.
set -euo pipefail
cd -- "$1"
paths=()
hashes=()
# sorted by path first; xargs and sha256sum keep that order. -z: NUL-terminated records, no name escaping
while IFS= read -r -d '' rec; do
  hashes+=("${rec:0:64}")
  p=${rec:66}
  paths+=("${p#./}")
done < <(find . -type f ! -empty -print0 | LC_ALL=C sort -z | xargs -0r sha256sum -z --)

declare -A count=() members=()
for i in "${!paths[@]}"; do
  h=${hashes[i]}
  count[$h]=$(( ${count[$h]:-0} + 1 ))
  members[$h]+="$i "
done
for i in "${!paths[@]}"; do
  h=${hashes[i]}
  first=${members[$h]%% *}
  [[ ${count[$h]} -ge 2 && $first == "$i" ]] || continue
  for j in ${members[$h]}; do
    printf '%s\0' "${paths[j]}"
  done
  printf '\0'
done
exit 0
