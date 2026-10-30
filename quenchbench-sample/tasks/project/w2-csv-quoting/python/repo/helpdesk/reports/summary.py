from ..config import PRIORITIES, STATUSES


def summarize(tickets):
    """Counts: every ticket by status, active tickets by priority and by assignee."""
    by_status = {s: 0 for s in STATUSES}
    by_priority = {p: 0 for p in PRIORITIES}
    by_assignee = {}
    for t in tickets:
        by_status[t.status] += 1
        if t.is_active():
            by_priority[t.priority] += 1
            who = t.assignee or "unassigned"
            by_assignee[who] = by_assignee.get(who, 0) + 1
    return {"status": by_status, "priority": by_priority, "assignee": by_assignee}
