#!/usr/bin/env bash
# publish.sh FILE: copies a markdown post to public/<slug>.html
set -euo pipefail
title=$(head -n 1 "$1" | sed 's/^# *//')
slug=$(bash "$(dirname "$0")/slugify.sh" -m 60 "$title")
mkdir -p public
cp "$1" "public/$slug.html"
echo "public/$slug.html"
