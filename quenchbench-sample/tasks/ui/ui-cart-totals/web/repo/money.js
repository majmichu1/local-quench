// Format an amount of cents as dollars.
export function formatMoney(cents) {
  return '$' + (cents / 100).toFixed(2);
}
