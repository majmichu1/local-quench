# helpers for archive.sh

archive_one() {
  # gzip file $1 into folder $2 as <name>.gz
  local name
  name=$(basename -- "$1")
  gzip -c -- "$1" > "$2/$name.gz"
}
