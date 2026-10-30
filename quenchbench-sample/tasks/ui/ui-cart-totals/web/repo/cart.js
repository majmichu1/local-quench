export const MAX_QTY = 10;
export const SHIPPING = 599;
export const FREE_SHIPPING_FROM = 5000;

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

export function discount(sub, code) {
  return code === 'SAVE10' ? sub * 0.1 : 0;
}

export function shipping(amount) {
  return amount > FREE_SHIPPING_FROM ? 0 : SHIPPING;
}

export function changeQty(items, sku, delta) {
  return items.map((item) => (item.sku === sku ? { ...item, qty: Math.max(0, item.qty + delta) } : item));
}
