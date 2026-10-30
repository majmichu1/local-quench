import { PRIORITIES, STATUSES } from '../config.mjs';

// Counts: every ticket by status, active tickets by priority and by assignee.
export function summarize(tickets) {
  const byStatus = Object.fromEntries(STATUSES.map((s) => [s, 0]));
  const byPriority = Object.fromEntries(PRIORITIES.map((p) => [p, 0]));
  const byAssignee = {};
  for (const t of tickets) {
    byStatus[t.status] += 1;
    if (t.isActive()) {
      byPriority[t.priority] += 1;
      const who = t.assignee || 'unassigned';
      byAssignee[who] = (byAssignee[who] ?? 0) + 1;
    }
  }
  return { status: byStatus, priority: byPriority, assignee: byAssignee };
}
