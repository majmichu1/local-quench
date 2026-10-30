import { INITIAL_ITEMS } from './data.js';
import { formatMoney } from './money.js';
import { MAX_QTY, subtotal, discount, shipping, changeQty } from './cart.js';

let items = INITIAL_ITEMS.map((item) => ({ ...item }));
let code = '';

const tbody = document.querySelector('#cart tbody');

function render() {
  tbody.innerHTML = '';
  for (const item of items) {
    const tr = document.createElement('tr');
    tr.dataset.sku = item.sku;
    tr.innerHTML = `<td class="name"></td><td class="price"></td>
      <td><button type="button" class="qty-dec" aria-label="Decrease">-</button>
      <span class="qty"></span>
      <button type="button" class="qty-inc" aria-label="Increase">+</button></td>
      <td class="line-total"></td>`;
    tr.querySelector('.name').textContent = item.name;
    tr.querySelector('.price').textContent = formatMoney(item.price);
    tr.querySelector('.qty').textContent = item.qty;
    tr.querySelector('.line-total').textContent = formatMoney(item.price * item.qty);
    tr.querySelector('.qty-inc').disabled = item.qty > MAX_QTY;
    tbody.appendChild(tr);
  }
  const sub = subtotal(items);
  const off = discount(sub, code);
  const ship = shipping(sub - off);
  document.getElementById('subtotal').textContent = formatMoney(sub);
  document.getElementById('discount').textContent = formatMoney(-off);
  document.getElementById('shipping').textContent = formatMoney(ship);
  document.getElementById('total').textContent = formatMoney(sub - off + ship);
  document.getElementById('cart-count').textContent = items.length;
}

tbody.addEventListener('click', (event) => {
  const tr = event.target.closest('tr');
  if (!tr) return;
  if (event.target.matches('.qty-inc')) items = changeQty(items, tr.dataset.sku, 1);
  if (event.target.matches('.qty-dec')) items = changeQty(items, tr.dataset.sku, -1);
  render();
});

document.getElementById('promo-form').addEventListener('submit', (event) => {
  event.preventDefault();
  code = document.getElementById('promo').value;
  document.getElementById('promo-msg').textContent = code === 'SAVE10' ? 'SAVE10 applied' : 'Invalid code';
  render();
});

render();
