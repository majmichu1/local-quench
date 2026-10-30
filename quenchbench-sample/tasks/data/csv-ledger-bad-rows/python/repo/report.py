import sys
from collections import defaultdict

from ledger import parse_ledger


def balances(rows):
    out = defaultdict(int)
    for r in rows:
        out[r["account"]] += r["amount_cents"]
    return dict(out)


if __name__ == "__main__":
    rows, errors = parse_ledger(open(sys.argv[1], encoding="utf-8").read())
    for line, reason in errors:
        print(f"line {line}: {reason}", file=sys.stderr)
    for acct, cents in sorted(balances(rows).items()):
        print(f"{acct}: {cents / 100:.2f}")
