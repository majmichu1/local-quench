set -e
git init -q -b main
git config user.name dev
git config user.email dev@example.com
git config commit.gpgsign false
mkdir -p 'shop'
cat > 'shop/cart.mjs' <<'FORGE_EOF'
import { unitPrice } from './pricing.mjs';

export function cartTotal(items) {
  const total = items.reduce((s, i) => s + unitPrice(i.sku) * i.qty, 0);
  const avg = total / items.length;
  if (Number.isNaN(avg)) throw new Error('bad cart');
  return Math.round(avg * items.length * 100) / 100;
}
FORGE_EOF
mkdir -p 'shop'
cat > 'shop/pricing.mjs' <<'FORGE_EOF'
export const PRICES = { apple: 0.5, pear: 0.75 };

export function unitPrice(sku) {
  return PRICES[sku];
}
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-01T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-01T10:00:00 +0000' git commit -qm 'initial'
cat > 'README.md' <<'FORGE_EOF'
# shop
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-02T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-02T10:00:00 +0000' git commit -qm 'add README'
git checkout -q -b dev
mkdir -p 'shop'
cat > 'shop/pricing.mjs' <<'FORGE_EOF'
export const PRICES = { apple: 0.5, pear: 0.75 };

export function unitPrice(sku) {
  return Math.round(PRICES[sku] * 110) / 100;
}
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-03T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-03T10:00:00 +0000' git commit -qm 'experimental: dynamic pricing'
mkdir -p 'shop'
cat > 'shop/cart.mjs' <<'FORGE_EOF'
import { unitPrice } from './pricing.mjs';

export function cartTotal(items) {
  const total = items.reduce((s, i) => s + unitPrice(i.sku) * i.qty, 0);
  return Math.round(total * 100) / 100;
}
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-04T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-04T10:00:00 +0000' git commit -qm 'fix: empty cart total is 0'
mkdir -p 'shop'
cat > 'shop/cart.mjs' <<'FORGE_EOF'
import { unitPrice } from './pricing.mjs';

export function cartTotal(items) {
  const total = items.reduce((s, i) => s + unitPrice(i.sku) * i.qty, 0);
  console.log('DEBUG', total);
  return Math.round(total * 100) / 100;
}
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-05T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-05T10:00:00 +0000' git commit -qm 'wip: debug logging'
git checkout -q main
cat > 'CHANGELOG.md' <<'FORGE_EOF'
- nothing yet
FORGE_EOF
git add -A && GIT_AUTHOR_DATE='2026-01-06T10:00:00 +0000' GIT_COMMITTER_DATE='2026-01-06T10:00:00 +0000' git commit -qm 'add CHANGELOG'
git rev-parse main > .git/forge-main-tip
git rev-parse dev > .git/forge-dev-tip
