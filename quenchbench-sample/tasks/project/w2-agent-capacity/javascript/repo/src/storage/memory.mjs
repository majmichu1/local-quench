import { TicketNotFound } from '../errors.mjs';

// Tickets and users, kept in memory. Tickets are stored by reference, not copied.
export class MemoryStore {
  constructor() {
    this._tickets = new Map();
    this._users = new Map();
    this._next = 1;
  }

  nextId() {
    return this._next++;
  }

  put(ticket) {
    this._tickets.set(ticket.id, ticket);
  }

  get(ticketId) {
    const ticket = this._tickets.get(ticketId);
    if (!ticket) throw new TicketNotFound(ticketId);
    return ticket;
  }

  all() {
    return [...this._tickets.values()].sort((a, b) => a.id - b.id);
  }

  addUser(user) {
    this._users.set(user.name, user);
  }

  user(name) {
    return this._users.get(name) ?? null;
  }

  agents() {
    return [...this._users.values()].filter((u) => u.role === 'agent').sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  }
}
