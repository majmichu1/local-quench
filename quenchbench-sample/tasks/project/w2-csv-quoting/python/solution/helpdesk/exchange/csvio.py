from ..errors import ValidationError

COLUMNS = ["id", "title", "requester", "priority", "status", "assignee", "tags", "created", "due"]


def quote(cell):
    if any(c in cell for c in ',"\r\n'):
        return '"' + cell.replace('"', '""') + '"'
    return cell


def export_csv(tickets):
    lines = [",".join(COLUMNS)]
    for t in tickets:
        row = [str(t.id), t.title, t.requester, t.priority, t.status, t.assignee, ";".join(t.tags),
               str(t.created), str(t.due)]
        lines.append(",".join(quote(c) for c in row))
    return "\n".join(lines) + "\n"


def parse_csv(text):
    rows, row, cell, quoted, i = [], [], "", False, 0
    while i < len(text):
        c = text[i]
        if quoted:
            if c == '"' and text[i + 1:i + 2] == '"':
                cell += '"'
                i += 1
            elif c == '"':
                quoted = False
            else:
                cell += c
        elif c == '"':
            quoted = True
        elif c == ",":
            row.append(cell)
            cell = ""
        elif c in "\r\n":
            if c == "\r" and text[i + 1:i + 2] == "\n":
                i += 1
            row.append(cell)
            cell = ""
            if any(row):
                rows.append(row)
            row = []
        else:
            cell += c
        i += 1
    if quoted:
        raise ValidationError("unterminated quote in csv")
    if cell or row:
        row.append(cell)
        if any(row):
            rows.append(row)
    return rows


def import_tickets(text, service):
    """Create a ticket per row; the columns title, requester, priority and tags are used."""
    rows = parse_csv(text)
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]
    made = []
    for raw in rows[1:]:
        row = dict(zip(header, raw))
        tags = [x for x in row.get("tags", "").split(";")]
        made.append(service.create(row.get("title", ""), row.get("requester", ""),
                                   row.get("priority") or "normal", tags))
    return made
