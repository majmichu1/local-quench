import { ManualClock } from './clock.mjs';
import { exportCsv, importTickets } from './exchange/csvio.mjs';
import { User } from './models/user.mjs';
import { Outbox } from './notify/outbox.mjs';
import { renderSummary } from './reports/format.mjs';
import { overdue } from './reports/overdue.mjs';
import { summarize } from './reports/summary.mjs';
import { run } from './search/filter.mjs';
import { parse } from './search/query.mjs';
import { Assigner } from './services/assignment.mjs';
import { SlaPolicy } from './services/sla.mjs';
import { TicketService } from './services/tickets.mjs';
import { MemoryStore } from './storage/memory.mjs';

// Wires the parts together; this is what the command line and the tests talk to.
export class Helpdesk {
  constructor(clock = null) {
    this.clock = clock ?? new ManualClock(0);
    this.store = new MemoryStore();
    this.outbox = new Outbox();
    this.sla = new SlaPolicy();
    this.assigner = new Assigner(this.store);
    this.tickets = new TicketService(this.store, this.clock, this.outbox, this.sla, this.assigner);
  }

  addAgent(name, skills = [], capacity = 5) {
    const user = new User(name, 'agent', skills.map((s) => s.trim().toLowerCase()).filter((s) => s), capacity);
    this.store.addUser(user);
    return user;
  }

  addRequester(name) {
    const user = new User(name, 'requester');
    this.store.addUser(user);
    return user;
  }

  search(text) {
    return run(this.store.all(), parse(text));
  }

  overdue() {
    return overdue(this.store.all(), this.clock.now());
  }

  summary() {
    return summarize(this.store.all());
  }

  exportCsv() {
    return exportCsv(this.store.all());
  }

  importCsv(text) {
    return importTickets(text, this.tickets);
  }

  report() {
    return renderSummary(this.summary());
  }
}
