import { ACTIVE } from '../config.mjs';

export class Ticket {
  constructor({ id, title, requester, priority, created, due, tags = [] }) {
    this.id = id;
    this.title = title;
    this.requester = requester;
    this.priority = priority;
    this.created = created;
    this.due = due;
    this.status = 'new';
    this.assignee = '';
    this.tags = tags;
    this.updated = 0;
    this.firstResponse = -1;
    this.resolvedAt = -1;
    this.comments = [];
    this.history = [];
  }

  isActive() {
    return ACTIVE.includes(this.status);
  }

  log(time, kind, detail = '') {
    this.history.push({ time, kind, detail });
    this.updated = time;
  }
}
