import { render } from './templates.mjs';

// Collects the messages the helpdesk wants to send. Nothing leaves the process.
export class Outbox {
  constructor() {
    this.messages = [];
  }

  send(to, key, time, values) {
    if (!to) return;
    this.messages.push({ to, text: render(key, values), time });
  }

  forUser(name) {
    return this.messages.filter((m) => m.to === name);
  }
}
