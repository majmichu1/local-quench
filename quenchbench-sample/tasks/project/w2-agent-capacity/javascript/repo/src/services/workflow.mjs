import { STATUSES } from '../config.mjs';
import { InvalidTransition, ValidationError } from '../errors.mjs';

export const TRANSITIONS = {
  new: ['open', 'pending', 'resolved', 'closed'],
  open: ['pending', 'resolved', 'closed'],
  pending: ['open', 'resolved', 'closed'],
  resolved: ['open', 'closed'],
  closed: [],
};

export function check(ticket, newStatus) {
  if (!STATUSES.includes(newStatus)) throw new ValidationError(`unknown status '${newStatus}'`);
  if (!TRANSITIONS[ticket.status].includes(newStatus)) {
    throw new InvalidTransition(`cannot move ticket ${ticket.id} from ${ticket.status} to ${newStatus}`);
  }
}
