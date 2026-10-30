export const FIELDS = ['status', 'priority', 'tag', 'assignee', 'requester'];

// Split a query like 'status:open -tag:vpn printer' into terms (all must match).
export function parse(text) {
  const terms = [];
  for (const token of text.split(/\s+/).filter((t) => t)) {
    const negated = token.startsWith('-') && token.length > 1;
    const body = negated ? token.slice(1) : token;
    const colon = body.indexOf(':');
    const name = colon >= 0 ? body.slice(0, colon).toLowerCase() : '';
    const value = colon >= 0 ? body.slice(colon + 1) : '';
    if (colon >= 0 && value && FIELDS.includes(name)) {
      terms.push({ field: name, value: value.toLowerCase(), negated });
    } else {
      terms.push({ field: 'text', value: body.toLowerCase(), negated });
    }
  }
  return terms;
}
