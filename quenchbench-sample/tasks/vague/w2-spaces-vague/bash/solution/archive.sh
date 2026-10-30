#!/usr/bin/env bash
# usage: archive.sh SRC_DIR DEST_DIR
# gzips every .log file of SRC_DIR into DEST_DIR (created when missing)
. "$(dirname "$0")/lib.sh"

src=$1
dest=$2
mkdir -p -- "$dest"

count=0
for f in "$src"/*.log; do
  [ -f "$f" ] || continue
  if archive_one "$f" "$dest"; then
    count=$((count + 1))
  fi
done
echo "archived $count files"
