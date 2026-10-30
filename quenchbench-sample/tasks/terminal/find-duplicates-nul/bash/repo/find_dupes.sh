#!/usr/bin/env bash
# find_dupes.sh DIR: print groups of files under DIR with identical contents.
# Output: each path followed by NUL, each group followed by one more NUL.
cd $1 || exit 1
files=( $(find . -type f ! -empty | sed 's|^\./||' | sort) )
declare -A seen
for ((i = 0; i < ${#files[@]}; i++)); do
  a=${files[i]}
  [ -n "${seen[$a]}" ] && continue
  group=$a
  for ((j = i + 1; j < ${#files[@]}; j++)); do
    b=${files[j]}
    [ -n "${seen[$b]}" ] && continue
    if cmp -s $a $b; then
      group="$group $b"
      seen[$b]=1
    fi
  done
  if [ "$group" != "$a" ]; then
    printf '%s\0' $group
    printf '\0'
  fi
done
