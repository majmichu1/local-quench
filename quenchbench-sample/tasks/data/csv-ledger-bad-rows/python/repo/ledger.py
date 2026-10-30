def parse_ledger(text):
    """Return (rows, errors), see the task description."""
    rows = []
    lines = text.split("\n")
    for line in lines[1:]:
        if not line:
            continue
        date, account, amount, memo = line.split(",")
        rows.append({"date": date, "account": account, "amount_cents": int(float(amount) * 100), "memo": memo})
    return rows, []
