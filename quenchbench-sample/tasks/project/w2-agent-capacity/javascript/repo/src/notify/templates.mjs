export const TEMPLATES = {
  created: 'Ticket #{id} received: {title}',
  assigned: 'Ticket #{id} assigned to {assignee}: {title}',
  status: 'Ticket #{id} is now {status}: {title}',
  comment: 'New reply on ticket #{id}: {title}',
};

export function render(key, values) {
  return TEMPLATES[key].replace(/\{(\w+)\}/g, (_, name) => String(values[name]));
}
