#!/usr/bin/env bash
# usage: slugify.sh [-m MAXLEN] TEXT
max=0
if [ "$1" = "-m" ]; then
  max=$2
  shift 2
fi
if [ $# -ne 1 ]; then
  echo "usage: slugify.sh [-m MAXLEN] TEXT" >&2
  exit 2
fi
slug=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | LC_ALL=C sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')
if [ "$max" -gt 0 ]; then
  slug=${slug:0:max}
  slug=${slug%-}
fi
if [ -z "$slug" ]; then
  exit 1
fi
printf '%s\n' "$slug"
