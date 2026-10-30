import test from 'node:test';
import assert from 'node:assert/strict';
import { LRUCache } from './cache.mjs';
import { memoize } from './memo.mjs';

// CPU seconds for a fixed piece of plain JS work (sorting 200k numbers and 200k Map writes): the time limit
// below scales with the machine and its load instead of being a fixed number of milliseconds (process CPU
// time, not wall time, so other programs running at the same time do not count).
const cpu = () => { const u = process.cpuUsage(); return (u.user + u.system) / 1e6; };
function baseline() {
  const t0 = cpu();
  const xs = Array.from({ length: 200000 }, (_, i) => (i * 2654435761) % 1000003);
  xs.sort((a, b) => a - b);
  const m = new Map();
  for (let i = 0; i < xs.length; i++) m.set(i, xs[i]);
  if (m.size !== xs.length) throw new Error('baseline');
  return cpu() - t0;
}

function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

test('basic behaviour', () => {
  const evicted = [];
  const c = new LRUCache(2, { onEvict: (k, v) => evicted.push([k, v]) });
  assert.equal(c.set('a', 1), c);
  c.set('b', 2);
  assert.equal(c.get('a'), 1);
  c.set('c', 3);
  assert.deepEqual(evicted, [['b', 2]]);
  assert.equal(c.get('b'), undefined);
  assert.deepEqual(c.keys(), ['a', 'c']);
  assert.equal(c.has('a'), true);
  c.set('d', 4);
  assert.deepEqual(evicted, [['b', 2], ['a', 1]], 'has() must not refresh');
  c.set('c', 30);
  assert.deepEqual(c.keys(), ['d', 'c']);
  assert.equal(c.size, 2);
  assert.equal(c.delete('d'), true);
  assert.equal(c.delete('d'), false);
  assert.equal(c.size, 1);
  assert.equal(evicted.length, 2);
  c.set('e', 5).set('f', 6);
  assert.deepEqual(evicted.at(-1), ['c', 30]);
});

test('capacity validation and key types', () => {
  for (const bad of [0, -1, 1.5, '3', undefined]) assert.throws(() => new LRUCache(bad), RangeError);
  const c = new LRUCache(3);
  const obj = {};
  c.set(obj, 'o').set(1, 'one').set('1', 'str');
  assert.equal(c.get(obj), 'o');
  assert.equal(c.get(1), 'one');
  assert.equal(c.get('1'), 'str');
  assert.deepEqual(c.keys(), [obj, 1, '1']);
  const one = new LRUCache(1);
  one.set('x', 1).set('y', 2);
  assert.deepEqual(one.keys(), ['y']);
});

test('random against a reference model', () => {
  const r = rng(8);
  for (let round = 0; round < 50; round++) {
    const cap = 1 + Math.floor(r() * 5);
    const ev = [];
    const c = new LRUCache(cap, { onEvict: (k, v) => ev.push(k + '=' + v) });
    let model = []; // [key, value], LRU first
    const mev = [];
    for (let i = 0; i < 60; i++) {
      const k = Math.floor(r() * 8);
      const op = r();
      if (op < 0.4) {
        const v = i;
        model = model.filter(([mk]) => mk !== k);
        model.push([k, v]);
        if (model.length > cap) { const [ok, ov] = model.shift(); mev.push(ok + '=' + ov); }
        c.set(k, v);
      } else if (op < 0.7) {
        const e = model.find(([mk]) => mk === k);
        if (e) { model = model.filter(([mk]) => mk !== k); model.push(e); }
        assert.equal(c.get(k), e ? e[1] : undefined);
      } else if (op < 0.85) {
        assert.equal(c.has(k), model.some(([mk]) => mk === k));
      } else {
        const had = model.some(([mk]) => mk === k);
        model = model.filter(([mk]) => mk !== k);
        assert.equal(c.delete(k), had);
      }
      assert.equal(c.size, model.length);
      assert.deepEqual(c.keys(), model.map(([mk]) => mk));
      assert.deepEqual(ev, mev);
    }
  }
});

test('memoize', () => {
  let calls = 0;
  const f = memoize((a, b) => { calls++; return a + b; }, 2);
  assert.equal(f(1, 2), 3);
  assert.equal(f(1, 2), 3);
  assert.equal(calls, 1);
  f(2, 3); f(3, 4);
  f(1, 2);
  assert.equal(calls, 4);
});

test('fast', () => {
  const r = rng(2);
  let evictions = 0;
  const c = new LRUCache(100000, { onEvict: () => { evictions++; } });
  const budget = 20 * baseline(); // here (4-core Xeon 2.1 GHz): baseline 0.16 s, reference 0.21 s, starting code 36.4 s
  const t0 = cpu();
  for (let i = 0; i < 150000; i++) c.set(i, i);
  let hits = 0;
  for (let i = 0; i < 300000; i++) {
    const k = Math.floor(r() * 200000);
    if (c.get(k) !== undefined) hits++;
    if (i % 3 === 0) c.set(k, i);
  }
  for (let i = 0; i < 50000; i++) c.delete(Math.floor(r() * 200000));
  const took = cpu() - t0;
  assert.equal(evictions >= 50000, true);
  assert.ok(hits > 0);
  assert.ok(c.size <= 100000);
  assert.ok(took < budget, `took ${took.toFixed(2)} s, budget ${budget.toFixed(2)} s`);
});
