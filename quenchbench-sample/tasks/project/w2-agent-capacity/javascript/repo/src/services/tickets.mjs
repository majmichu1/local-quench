import { PRIORITIES } from '../config.mjs';
import { ValidationError } from '../errors.mjs';
import { Ticket } from '../models/ticket.mjs';
import * as workflow from './workflow.mjs';

export class TicketService {
  constructor(store, clock, outbox, sla, assigner) {
    this.store = store;
    this.clock = clock;
    this.outbox = outbox;
    this.sla = sla;
    this.assigner = assigner;
  }

  get(ticketId) {
    return this.store.get(ticketId);
  }

  create(title, requester, priority = 'normal', tags = []) {
    title = title.trim();
    if (!title) throw new ValidationError('title is required');
    if (!PRIORITIES.includes(priority)) throw new ValidationError(`unknown priority '${priority}'`);
    const now = this.clock.now();
    const clean = [...new Set(tags.map((x) => x.trim().toLowerCase()).filter((x) => x))].sort();
    const ticket = new Ticket({
      id: this.store.nextId(), title, requester, priority, created: now,
      due: this.sla.dueFor(now, priority), tags: clean,
    });
    ticket.log(now, 'created');
    this.store.put(ticket);
    this.outbox.send(requester, 'created', now, { id: ticket.id, title: ticket.title });
    return ticket;
  }

  assign(ticketId, agent) {
    const ticket = this.store.get(ticketId);
    const user = this.store.user(agent);
    if (user === null || user.role !== 'agent') throw new ValidationError(`unknown agent '${agent}'`);
    const now = this.clock.now();
    ticket.assignee = agent;
    ticket.log(now, 'assigned', agent);
    this.outbox.send(agent, 'assigned', now, { id: ticket.id, title: ticket.title, assignee: agent });
    return ticket;
  }

  autoAssign(ticketId) {
    const ticket = this.store.get(ticketId);
    const name = this.assigner.pick(ticket);
    if (name) this.assign(ticketId, name);
    return name;
  }

  changeStatus(ticketId, status) {
    const ticket = this.store.get(ticketId);
    workflow.check(ticket, status);
    const now = this.clock.now();
    const old = ticket.status;
    ticket.status = status;
    if (status === 'resolved') ticket.resolvedAt = now;
    else if (old === 'resolved') ticket.resolvedAt = -1;
    ticket.log(now, 'status', `${old}->${status}`);
    this.outbox.send(ticket.requester, 'status', now, { id: ticket.id, title: ticket.title, status });
    return ticket;
  }

  setPriority(ticketId, priority) {
    const ticket = this.store.get(ticketId);
    if (!PRIORITIES.includes(priority)) throw new ValidationError(`unknown priority '${priority}'`);
    const old = ticket.priority;
    ticket.priority = priority;
    ticket.due = ticket.created + this.sla.minutes[priority];
    ticket.log(this.clock.now(), 'priority', `${old}->${priority}`);
    return ticket;
  }

  addTag(ticketId, tag) {
    const ticket = this.store.get(ticketId);
    tag = tag.trim().toLowerCase();
    if (!tag) throw new ValidationError('tag is empty');
    if (!ticket.tags.includes(tag)) {
      ticket.tags.push(tag);
      ticket.tags.sort();
      ticket.log(this.clock.now(), 'tag+', tag);
    }
    return ticket;
  }

  removeTag(ticketId, tag) {
    const ticket = this.store.get(ticketId);
    tag = tag.trim().toLowerCase();
    const at = ticket.tags.indexOf(tag);
    if (at >= 0) {
      ticket.tags.splice(at, 1);
      ticket.log(this.clock.now(), 'tag-', tag);
    }
    return ticket;
  }

  comment(ticketId, author, text, isPublic = true) {
    const ticket = this.store.get(ticketId);
    text = text.trim();
    if (!text) throw new ValidationError('comment is empty');
    const now = this.clock.now();
    ticket.comments.push({ author, text, public: isPublic, time: now });
    const user = this.store.user(author);
    const byAgent = user !== null && user.role === 'agent';
    if (byAgent && isPublic && ticket.firstResponse < 0) ticket.firstResponse = now;
    ticket.log(now, 'comment', author);
    if (isPublic) {
      const target = byAgent ? ticket.requester : ticket.assignee;
      this.outbox.send(target, 'comment', now, { id: ticket.id, title: ticket.title });
    }
    return ticket;
  }
}
