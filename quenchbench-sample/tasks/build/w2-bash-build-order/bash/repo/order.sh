#!/usr/bin/env bash
set -euo pipefail

file=${1:-}
target=${2:-}
if [[ -z $file ]]; then
  echo "usage: order.sh FILE [TARGET]" >&2
  exit 64
fi

declare -A deps
nodes=()
count=0

add_node() {
  if [[ -z ${deps[$1]} ]]; then
    deps[$1]=" "
    nodes+=("$1")
    ((count++))
  fi
}

# strip comments and blank lines
cleaned=$(grep -v '^#' "$file" | grep -v '^$')
while IFS= read -r line; do
  line=${line%%#*}
  name=${line%%:*}
  name=${name//[[:space:]]/}
  add_node "$name"
  for d in ${line#*:}; do
    add_node "$d"
    deps[$name]+=" $d"
  done
done <<< "$cleaned"

declare -A want
if [[ -n $target ]]; then
  if [[ -z ${deps[$target]} ]]; then
    echo "unknown target: $target" >&2
    exit 2
  fi
  stack=("$target")
  while [[ ${#stack[@]} -gt 0 ]]; do
    n=${stack[-1]}
    unset 'stack[-1]'
    [[ -z ${want[$n]} ]] || continue
    want[$n]=1
    for d in ${deps[$n]}; do stack+=("$d"); done
  done
else
  for n in "${nodes[@]}"; do want[$n]=1; done
fi

declare -A done_
remaining=${#want[@]}
while [[ $remaining -gt 0 ]]; do
  pick=""
  for n in "${!want[@]}"; do
    [[ -z ${done_[$n]} ]] || continue
    ready=1
    for d in ${deps[$n]}; do
      [[ -n ${done_[$d]} ]] || ready=0
    done
    [[ $ready -eq 1 && ( -z $pick || $n < $pick ) ]] && pick=$n
  done
  if [[ -z $pick ]]; then
    left=()
    for n in "${!want[@]}"; do [[ -n ${done_[$n]} ]] || left+=("$n"); done
    echo "cycle: ${left[*]}" >&2
    exit 3
  fi
  done_[$pick]=1
  echo "$pick"
  ((remaining--))
done
