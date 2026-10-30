from dataclasses import dataclass

FIELDS = ("status", "priority", "tag", "assignee", "requester")


@dataclass
class Term:
    field: str  # one of FIELDS, or "text" for a word of the title
    value: str
    negated: bool = False


def parse(text):
    """Split a query like 'status:open -tag:vpn printer' into terms (all must match)."""
    terms = []
    for token in text.split():
        negated = token.startswith("-") and len(token) > 1
        body = token[1:] if negated else token
        name, sep, value = body.partition(":")
        if sep and value and name.lower() in FIELDS:
            terms.append(Term(name.lower(), value.lower(), negated))
        else:
            terms.append(Term("text", body.lower(), negated))
    return terms
