"""Fixed vocabulary of the helpdesk. Times everywhere are whole minutes on a clock that starts at 0."""

PRIORITIES = ("low", "normal", "high", "urgent")
STATUSES = ("new", "open", "pending", "resolved", "closed")
ACTIVE = ("new", "open", "pending")

# minutes a ticket may take before it is overdue, by priority
SLA_MINUTES = {"low": 4320, "normal": 1440, "high": 480, "urgent": 120}
