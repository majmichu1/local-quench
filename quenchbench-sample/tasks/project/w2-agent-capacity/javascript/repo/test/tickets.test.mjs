import test from 'node:test';
import assert from 'node:assert/strict';
import { Helpdesk } from '../src/index.mjs';
import { InvalidTransition, TicketNotFound, ValidationError } from '../src/errors.mjs';

function desk() {
  const hd = new Helpdesk();
  hd.addAgent('ana', ['network']);
  hd.addAgent('ben');
  hd.addRequester('zoe');
  return hd;
}

test('create sets due from priority', () => {
  const hd = desk();
  hd.clock.set(100);
  const t = hd.tickets.create('Printer jammed', 'zoe', 'high');
  assert.deepEqual([t.status, t.created, t.due], ['new', 100, 580]);
  assert.equal(hd.outbox.forUser('zoe')[0].text, 'Ticket #1 received: Printer jammed');
});

test('validation', () => {
  const hd = desk();
  assert.throws(() => hd.tickets.create('  ', 'zoe'), ValidationError);
  assert.throws(() => hd.tickets.create('x', 'zoe', 'critical'), ValidationError);
  assert.throws(() => hd.tickets.get(9), TicketNotFound);
});

test('status flow', () => {
  const hd = desk();
  const t = hd.tickets.create('x', 'zoe');
  hd.tickets.changeStatus(t.id, 'open');
  hd.tickets.changeStatus(t.id, 'resolved');
  assert.equal(t.resolvedAt, 0);
  hd.tickets.changeStatus(t.id, 'closed');
  assert.throws(() => hd.tickets.changeStatus(t.id, 'open'), InvalidTransition);
});

test('comment sets first response', () => {
  const hd = desk();
  const t = hd.tickets.create('x', 'zoe');
  hd.tickets.assign(t.id, 'ana');
  hd.clock.advance(30);
  hd.tickets.comment(t.id, 'zoe', 'hello');
  assert.equal(t.firstResponse, -1);
  hd.tickets.comment(t.id, 'ana', 'on it');
  assert.equal(t.firstResponse, 30);
});

test('tags and auto assign', () => {
  const hd = desk();
  const t = hd.tickets.create('VPN', 'zoe', 'normal', ['Network', ' vpn ']);
  assert.deepEqual(t.tags, ['network', 'vpn']);
  assert.equal(hd.tickets.autoAssign(t.id), 'ana');
});
