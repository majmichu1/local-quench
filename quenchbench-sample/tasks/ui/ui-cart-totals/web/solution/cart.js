export const MAX_QTY = 10;
export const SHIPPING = 599;
export const FREE_SHIPPING_FROM = 5000;

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

export function normalizeCode(code) {
  return code.trim().toUpperCase();
}

export function discount(sub, code) {
  return normalizeCode(code) === 'SAVE10' ? Math.round(sub / 10) : 0;
}

export function shipping(amount, empty) {
  if (empty) return 0;
  return amount >= FREE_SHIPPING_FROM ? 0 : SHIPPING;
}

export function changeQty(items, sku, delta) {
  return items
    .map((item) => (item.sku === sku ? { ...item, qty: Math.min(MAX_QTY, item.qty + delta) } : item))
    .filter((item) => item.qty > 0);
}
