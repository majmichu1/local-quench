import test from 'node:test';
import assert from 'node:assert/strict';
import { Helpdesk } from './src/index.mjs';

function desk() {
  const hd = new Helpdesk();
  hd.addAgent('ana', ['network'], 1);
  hd.addAgent('ben', [], 2);
  hd.addAgent('cy', ['network'], 0);
  hd.addRequester('zoe');
  return hd;
}

test('full agents are skipped', () => {
  const t = desk().tickets;
  const t1 = t.create('one', 'zoe', 'normal', ['network']);
  assert.equal(t.autoAssign(t1.id), 'ana');
  const t2 = t.create('two', 'zoe', 'normal', ['network']);
  assert.equal(t.autoAssign(t2.id), 'ben');
  const t3 = t.create('three', 'zoe');
  assert.equal(t.autoAssign(t3.id), 'ben');
  assert.deepEqual([t1, t2, t3].map((x) => x.assignee), ['ana', 'ben', 'ben']);
});

test('nobody has room: nothing changes', () => {
  const hd = desk();
  const t = hd.tickets;
  for (const title of ['one', 'two', 'three']) t.autoAssign(t.create(title, 'zoe', 'normal', ['network']).id);
  const t4 = t.create('four', 'zoe', 'normal', ['network']);
  hd.clock.advance(50);
  const before = [hd.outbox.messages.length, t4.history.length, t4.updated];
  assert.equal(t.autoAssign(t4.id), '');
  assert.equal(t4.assignee, '');
  assert.deepEqual([hd.outbox.messages.length, t4.history.length, t4.updated], before);
});

test('resolving and closing free a slot', () => {
  const t = desk().tickets;
  const t1 = t.create('one', 'zoe', 'normal', ['network']);
  t.autoAssign(t1.id);
  const t2 = t.create('two', 'zoe', 'normal');
  const t3 = t.create('three', 'zoe', 'normal');
  t.autoAssign(t2.id);
  t.autoAssign(t3.id);
  const t4 = t.create('four', 'zoe', 'normal', ['network']);
  assert.equal(t.autoAssign(t4.id), '');
  t.changeStatus(t1.id, 'resolved');
  assert.equal(t.autoAssign(t4.id), 'ana');
  const t5 = t.create('five', 'zoe', 'normal', ['network']);
  assert.equal(t.autoAssign(t5.id), '');
  t.changeStatus(t4.id, 'closed');
  assert.equal(t.autoAssign(t5.id), 'ana');
});

test('manual assignment ignores capacity', () => {
  const t = desk().tickets;
  for (const title of ['one', 'two', 'three']) {
    const tk = t.create(title, 'zoe');
    t.assign(tk.id, 'cy');
    assert.equal(tk.assignee, 'cy');
  }
  const extra = t.create('four', 'zoe', 'normal', ['network']);
  assert.equal(t.autoAssign(extra.id), 'ana');
});

test('skill preference and load among agents with room', () => {
  const hd = new Helpdesk();
  hd.addAgent('bob', ['db'], 3);
  hd.addAgent('amy', [], 3);
  hd.addRequester('zoe');
  const t = hd.tickets;
  assert.equal(t.autoAssign(t.create('one', 'zoe', 'normal', ['db']).id), 'bob');
  assert.equal(t.autoAssign(t.create('two', 'zoe', 'normal', ['db']).id), 'bob');
  assert.equal(t.autoAssign(t.create('three', 'zoe').id), 'amy');
});

test('create with autoAssign', () => {
  const hd = desk();
  const t = hd.tickets;
  const a = t.create('one', 'zoe', 'high', ['network'], true);
  assert.equal(a.assignee, 'ana');
  assert.equal(hd.outbox.forUser('ana')[0].text, 'Ticket #1 assigned to ana: one');
  assert.equal(t.create('two', 'zoe', 'high', ['network'], true).assignee, 'ben');
  t.create('three', 'zoe', 'normal', [], true);
  assert.equal(t.create('four', 'zoe', 'normal', ['network'], true).assignee, '');
  assert.equal(t.create('five', 'zoe').assignee, '');
});
