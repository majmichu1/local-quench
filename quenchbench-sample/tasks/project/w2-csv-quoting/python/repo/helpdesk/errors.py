class HelpdeskError(Exception):
    """Base class of every error raised on purpose by the helpdesk."""


class TicketNotFound(HelpdeskError):
    def __init__(self, ticket_id):
        super().__init__(f"ticket {ticket_id} not found")
        self.ticket_id = ticket_id


class InvalidTransition(HelpdeskError):
    pass


class ValidationError(HelpdeskError):
    pass
