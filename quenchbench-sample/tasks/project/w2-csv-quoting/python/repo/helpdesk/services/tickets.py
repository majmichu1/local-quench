from ..config import PRIORITIES
from ..errors import ValidationError
from ..models.ticket import Comment, Ticket
from . import workflow


class TicketService:
    def __init__(self, store, clock, outbox, sla, assigner):
        self.store = store
        self.clock = clock
        self.outbox = outbox
        self.sla = sla
        self.assigner = assigner

    def get(self, ticket_id):
        return self.store.get(ticket_id)

    def create(self, title, requester, priority="normal", tags=()):
        title = title.strip()
        if not title:
            raise ValidationError("title is required")
        if priority not in PRIORITIES:
            raise ValidationError(f"unknown priority {priority!r}")
        now = self.clock.now()
        clean = sorted({x.strip().lower() for x in tags if x.strip()})
        ticket = Ticket(id=self.store.next_id(), title=title, requester=requester, priority=priority,
                        created=now, due=self.sla.due_for(now, priority), tags=clean)
        ticket.log(now, "created")
        self.store.put(ticket)
        self.outbox.send(requester, "created", now, id=ticket.id, title=ticket.title)
        return ticket

    def assign(self, ticket_id, agent):
        ticket = self.store.get(ticket_id)
        user = self.store.user(agent)
        if user is None or user.role != "agent":
            raise ValidationError(f"unknown agent {agent!r}")
        now = self.clock.now()
        ticket.assignee = agent
        ticket.log(now, "assigned", agent)
        self.outbox.send(agent, "assigned", now, id=ticket.id, title=ticket.title, assignee=agent)
        return ticket

    def auto_assign(self, ticket_id):
        ticket = self.store.get(ticket_id)
        name = self.assigner.pick(ticket)
        if name:
            self.assign(ticket_id, name)
        return name

    def change_status(self, ticket_id, status):
        ticket = self.store.get(ticket_id)
        workflow.check(ticket, status)
        now = self.clock.now()
        old = ticket.status
        ticket.status = status
        if status == "resolved":
            ticket.resolved_at = now
        elif old == "resolved":
            ticket.resolved_at = -1
        ticket.log(now, "status", f"{old}->{status}")
        self.outbox.send(ticket.requester, "status", now, id=ticket.id, title=ticket.title, status=status)
        return ticket

    def set_priority(self, ticket_id, priority):
        ticket = self.store.get(ticket_id)
        if priority not in PRIORITIES:
            raise ValidationError(f"unknown priority {priority!r}")
        old = ticket.priority
        ticket.priority = priority
        ticket.due = ticket.created + self.sla.minutes[priority]
        ticket.log(self.clock.now(), "priority", f"{old}->{priority}")
        return ticket

    def add_tag(self, ticket_id, tag):
        ticket = self.store.get(ticket_id)
        tag = tag.strip().lower()
        if not tag:
            raise ValidationError("tag is empty")
        if tag not in ticket.tags:
            ticket.tags.append(tag)
            ticket.tags.sort()
            ticket.log(self.clock.now(), "tag+", tag)
        return ticket

    def remove_tag(self, ticket_id, tag):
        ticket = self.store.get(ticket_id)
        tag = tag.strip().lower()
        if tag in ticket.tags:
            ticket.tags.remove(tag)
            ticket.log(self.clock.now(), "tag-", tag)
        return ticket

    def comment(self, ticket_id, author, text, public=True):
        ticket = self.store.get(ticket_id)
        text = text.strip()
        if not text:
            raise ValidationError("comment is empty")
        now = self.clock.now()
        ticket.comments.append(Comment(author, text, public, now))
        user = self.store.user(author)
        by_agent = user is not None and user.role == "agent"
        if by_agent and public and ticket.first_response < 0:
            ticket.first_response = now
        ticket.log(now, "comment", author)
        if public:
            target = ticket.requester if by_agent else ticket.assignee
            self.outbox.send(target, "comment", now, id=ticket.id, title=ticket.title)
        return ticket
