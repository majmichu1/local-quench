def fmt_time(minutes):
    return f"d{minutes // 1440} {minutes % 1440 // 60:02d}:{minutes % 60:02d}"


def render_table(headers, rows):
    widths = [max(len(str(c)) for c in col) for col in zip(headers, *rows)] if rows else [len(h) for h in headers]
    lines = ["  ".join(str(c).ljust(w) for c, w in zip(headers, widths)).rstrip()]
    for row in rows:
        lines.append("  ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())
    return "\n".join(lines)


def render_summary(summary):
    rows = [(name, count) for name, count in summary["status"].items()]
    text = render_table(("status", "tickets"), rows)
    rows = sorted(summary["assignee"].items())
    return text + "\n\n" + render_table(("assignee", "active"), rows)
