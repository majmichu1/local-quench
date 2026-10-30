const pad2 = (n) => String(n).padStart(2, '0');

export function fmtTime(minutes) {
  return `d${Math.floor(minutes / 1440)} ${pad2(Math.floor((minutes % 1440) / 60))}:${pad2(minutes % 60)}`;
}

export function renderTable(headers, rows) {
  const widths = headers.map((h, i) => Math.max(String(h).length, ...rows.map((r) => String(r[i]).length)));
  const line = (cells) => cells.map((c, i) => String(c).padEnd(widths[i])).join('  ').trimEnd();
  return [line(headers), ...rows.map(line)].join('\n');
}

export function renderSummary(summary) {
  const text = renderTable(['status', 'tickets'], Object.entries(summary.status));
  const rows = Object.entries(summary.assignee).sort((a, b) => (a[0] < b[0] ? -1 : 1));
  return `${text}\n\n${renderTable(['assignee', 'active'], rows)}`;
}
