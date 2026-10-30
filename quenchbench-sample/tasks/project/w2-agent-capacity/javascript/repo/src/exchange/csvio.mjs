import { ValidationError } from '../errors.mjs';

export const COLUMNS = ['id', 'title', 'requester', 'priority', 'status', 'assignee', 'tags', 'created', 'due'];

export function quote(cell) {
  if (/[,"\r\n]/.test(cell)) return `"${cell.replaceAll('"', '""')}"`;
  return cell;
}

export function exportCsv(tickets) {
  const lines = [COLUMNS.join(',')];
  for (const t of tickets) {
    const row = [String(t.id), t.title, t.requester, t.priority, t.status, t.assignee, t.tags.join(';'),
      String(t.created), String(t.due)];
    lines.push(row.map(quote).join(','));
  }
  return lines.join('\n') + '\n';
}

export function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;
  const endRow = () => {
    row.push(cell);
    cell = '';
    if (row.some((c) => c !== '')) rows.push(row);
    row = [];
  };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        cell += '"';
        i++;
      } else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') {
      row.push(cell);
      cell = '';
    } else if (c === '\r' || c === '\n') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      endRow();
    } else cell += c;
  }
  if (quoted) throw new ValidationError('unterminated quote in csv');
  if (cell !== '' || row.length > 0) endRow();
  return rows;
}

// Create a ticket per row; the columns title, requester, priority and tags are used.
export function importTickets(text, service) {
  const rows = parseCsv(text);
  if (rows.length === 0) return [];
  const header = rows[0].map((h) => h.trim().toLowerCase());
  return rows.slice(1).map((raw) => {
    const row = {};
    header.forEach((name, i) => { if (i < raw.length) row[name] = raw[i]; });
    const tags = (row.tags ?? '').split(';');
    return service.create(row.title ?? '', row.requester ?? '', row.priority || 'normal', tags);
  });
}
