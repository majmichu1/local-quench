import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { cartTotal } from './shop/cart.mjs';

const git = (...a) => execFileSync('git', a, { encoding: 'utf8' }).trim();
const orig = (n) => readFileSync('.git/' + n, 'utf8').trim();

test('behaviour', () => {
  assert.equal(cartTotal([]), 0);
  assert.equal(cartTotal([{ sku: 'apple', qty: 3 }, { sku: 'pear', qty: 2 }]), 3);
  assert.ok(!readFileSync('shop/cart.mjs', 'utf8').includes('DEBUG'));
});

test('history', () => {
  assert.equal(git('rev-parse', '--abbrev-ref', 'HEAD'), 'main');
  assert.equal(git('log', '-1', '--format=%P'), orig('forge-main-tip'), 'expected one new commit on main');
  assert.match(git('log', '-1', '--format=%s'), /empty cart/);
  assert.equal(git('rev-parse', 'dev'), orig('forge-dev-tip'), 'dev must not change');
  assert.equal(git('status', '--porcelain', '--untracked-files=no'), '');
});
