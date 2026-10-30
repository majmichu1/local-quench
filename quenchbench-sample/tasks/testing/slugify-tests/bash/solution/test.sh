#!/usr/bin/env bash
fail=0
check() { # check EXPECTED_OUTPUT EXPECTED_STATUS ARGS...
  local want=$1 want_status=$2
  shift 2
  local got status
  got=$(bash slugify.sh "$@" 2>/dev/null)
  status=$?
  if [ "$got" != "$want" ] || [ "$status" != "$want_status" ]; then
    echo "FAIL: slugify.sh $* -> '$got' ($status), want '$want' ($want_status)"
    fail=1
  fi
}
check "hello-world" 0 "Hello World"
check "hello-world" 0 "  Hello,   World!  "
check "a-b" 0 "a  --  b"
check "release-2-0-1" 0 "Release 2.0.1"
check "abc123" 0 "ABC123"
check "x" 0 "---x---"
check "" 1 "!!!"
check "" 1 ""
check "hello" 0 -m 5 "Hello World"
check "hello" 0 -m 6 "Hello World"
check "hello-w" 0 -m 7 "Hello World"
check "hello-world" 0 -m 0 "Hello World"
check "" 2
check "" 2 a b
exit $fail
