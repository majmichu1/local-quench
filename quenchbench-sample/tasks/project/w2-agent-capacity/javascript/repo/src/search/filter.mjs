export function matches(ticket, term) {
  let hit;
  if (term.field === 'text') hit = ticket.title.toLowerCase().includes(term.value);
  else if (term.field === 'tag') hit = ticket.tags.map((x) => x.toLowerCase()).includes(term.value);
  else hit = String(ticket[term.field]).toLowerCase() === term.value;
  return hit !== term.negated;
}

export function run(tickets, terms) {
  return tickets.filter((t) => terms.every((term) => matches(t, term)));
}
