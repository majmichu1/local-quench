#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

if [[ $# -lt 1 ]]; then
  echo "usage: order.sh FILE [TARGET]" >&2
  exit 64
fi
file=$1
target=${2:-}
if [[ ! -r $file ]]; then
  echo "cannot read $file" >&2
  exit 64
fi

declare -A deps=()
nodes=()
add_node() {
  if [[ -z ${deps[$1]+x} ]]; then
    deps[$1]=""
    nodes+=("$1")
  fi
}

while IFS= read -r line || [[ -n $line ]]; do
  line=${line%%#*}
  [[ $line == *:* ]] || continue
  name=${line%%:*}
  name=${name//[[:space:]]/}
  [[ -n $name ]] || continue
  add_node "$name"
  for d in ${line#*:}; do
    add_node "$d"
    deps[$name]+=" $d"
  done
done < "$file"

declare -A want=()
if [[ -n $target ]]; then
  if [[ -z ${deps[$target]+x} ]]; then
    echo "unknown target: $target" >&2
    exit 2
  fi
  stack=("$target")
  while [[ ${#stack[@]} -gt 0 ]]; do
    n=${stack[-1]}
    unset 'stack[-1]'
    [[ -z ${want[$n]+x} ]] || continue
    want[$n]=1
    for d in ${deps[$n]}; do stack+=("$d"); done
  done
else
  for n in "${nodes[@]+"${nodes[@]}"}"; do want[$n]=1; done
fi

declare -A done_=()
remaining=${#want[@]}
while [[ $remaining -gt 0 ]]; do
  pick=""
  for n in "${!want[@]}"; do
    [[ -z ${done_[$n]+x} ]] || continue
    ready=1
    for d in ${deps[$n]}; do
      if [[ -z ${done_[$d]+x} ]]; then ready=0; break; fi
    done
    if [[ $ready -eq 1 ]] && { [[ -z $pick ]] || [[ $n < $pick ]]; }; then pick=$n; fi
  done
  if [[ -z $pick ]]; then
    left=()
    for n in "${!want[@]}"; do [[ -n ${done_[$n]+x} ]] || left+=("$n"); done
    echo "cycle: $(printf '%s\n' "${left[@]}" | sort | paste -sd' ')" >&2
    exit 3
  fi
  done_[$pick]=1
  echo "$pick"
  remaining=$((remaining - 1))
done
