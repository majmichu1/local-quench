import re

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
AMOUNT = re.compile(r"(-?)(\d+)(?:\.(\d{2}))?")


def split_records(text):
    """Yield (line, fields) per record; fields is None for an unterminated quote."""
    fields, cur = [], []
    line = start = 1
    in_quotes, at_start = False, True
    content = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                if c == "\n":
                    line += 1
                cur.append(c)
        elif c == '"' and at_start:
            in_quotes, at_start, content = True, False, True
        elif c == ",":
            fields.append("".join(cur))
            cur, at_start, content = [], True, True
        elif c == "\n" or (c == "\r" and i + 1 < n and text[i + 1] == "\n"):
            if c == "\r":
                i += 1
            if content:
                fields.append("".join(cur))
                yield start, fields
            fields, cur, at_start, content = [], [], True, False
            line += 1
            start = line
        else:
            cur.append(c)
            at_start, content = False, True
        i += 1
    if in_quotes:
        yield start, None
    elif content:
        fields.append("".join(cur))
        yield start, fields


def parse_ledger(text):
    """Return (rows, errors), see the task description."""
    rows, errors = [], []
    first = True
    for line, fields in split_records(text):
        if first:
            first = False
            if fields is not None:
                continue
        if fields is None:
            errors.append((line, "unterminated quote"))
            continue
        if len(fields) != 4:
            errors.append((line, "field count"))
            continue
        date, account, amount, memo = fields
        m = AMOUNT.fullmatch(amount)
        if not DATE.fullmatch(date):
            errors.append((line, "bad date"))
        elif not account.strip():
            errors.append((line, "empty account"))
        elif not m:
            errors.append((line, "bad amount"))
        else:
            cents = int(m.group(2)) * 100 + int(m.group(3) or 0)
            rows.append({"date": date, "account": account.strip(), "amount_cents": -cents if m.group(1) else cents,
                         "memo": memo.strip()})
    return rows, errors
