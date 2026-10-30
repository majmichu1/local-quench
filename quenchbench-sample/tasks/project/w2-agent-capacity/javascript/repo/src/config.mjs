// Fixed vocabulary of the helpdesk. Times everywhere are whole minutes on a clock that starts at 0.

export const PRIORITIES = ['low', 'normal', 'high', 'urgent'];
export const STATUSES = ['new', 'open', 'pending', 'resolved', 'closed'];
export const ACTIVE = ['new', 'open', 'pending'];

// minutes a ticket may take before it is overdue, by priority
export const SLA_MINUTES = { low: 4320, normal: 1440, high: 480, urgent: 120 };
