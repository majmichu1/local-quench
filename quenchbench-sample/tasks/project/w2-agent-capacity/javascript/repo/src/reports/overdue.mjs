// Active tickets whose due time has passed, most overdue first (ties by id).
export function overdue(tickets, now) {
  return tickets.filter((t) => t.isActive() && t.due < now).sort((a, b) => a.due - b.due || a.id - b.id);
}
