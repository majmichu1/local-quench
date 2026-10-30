export class HelpdeskError extends Error {
  constructor(message) {
    super(message);
    this.name = new.target.name;
  }
}

export class TicketNotFound extends HelpdeskError {
  constructor(ticketId) {
    super(`ticket ${ticketId} not found`);
    this.ticketId = ticketId;
  }
}

export class InvalidTransition extends HelpdeskError {}

export class ValidationError extends HelpdeskError {}
