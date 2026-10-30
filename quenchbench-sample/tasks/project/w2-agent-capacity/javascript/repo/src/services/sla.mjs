import { SLA_MINUTES } from '../config.mjs';

// Decides when a ticket is due.
export class SlaPolicy {
  constructor(minutes = SLA_MINUTES) {
    this.minutes = { ...minutes };
  }

  dueFor(created, priority) {
    return created + this.minutes[priority];
  }
}
