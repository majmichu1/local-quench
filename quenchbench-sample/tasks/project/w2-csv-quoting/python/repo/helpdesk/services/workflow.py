from ..config import STATUSES
from ..errors import InvalidTransition, ValidationError

TRANSITIONS = {
    "new": {"open", "pending", "resolved", "closed"},
    "open": {"pending", "resolved", "closed"},
    "pending": {"open", "resolved", "closed"},
    "resolved": {"open", "closed"},
    "closed": set(),
}


def check(ticket, new_status):
    if new_status not in STATUSES:
        raise ValidationError(f"unknown status {new_status!r}")
    if new_status not in TRANSITIONS[ticket.status]:
        raise InvalidTransition(f"cannot move ticket {ticket.id} from {ticket.status} to {new_status}")
