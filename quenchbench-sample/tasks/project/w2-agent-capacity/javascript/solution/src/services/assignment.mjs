import { ACTIVE } from '../config.mjs';

// Picks an agent for a ticket: skilled agents first, then the least loaded one.
export class Assigner {
  constructor(store) {
    this.store = store;
  }

  load(agent) {
    return this.store.all().filter((t) => t.assignee === agent.name && ACTIVE.includes(t.status)).length;
  }

  pick(ticket) {
    const agents = this.store.agents().filter((a) => this.load(a) < a.capacity);
    if (agents.length === 0) return '';
    const skilled = agents.filter((a) => ticket.tags.some((tag) => a.skills.includes(tag)));
    const pool = skilled.length > 0 ? skilled : agents;
    let best = null;
    let bestLoad = 0;
    for (const agent of pool) {
      const load = this.load(agent);
      if (best === null || load < bestLoad || (load === bestLoad && agent.name < best.name)) {
        best = agent;
        bestLoad = load;
      }
    }
    return best.name;
  }
}
