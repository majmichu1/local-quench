// Format an amount of cents as dollars: 123456 -> "$1,234.56", -1930 -> "-$19.30".
export function formatMoney(cents) {
  const value = Math.round(cents);
  const sign = value < 0 ? '-' : '';
  const abs = Math.abs(value);
  const dollars = Math.floor(abs / 100).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return `${sign}$${dollars}.${String(abs % 100).padStart(2, '0')}`;
}
