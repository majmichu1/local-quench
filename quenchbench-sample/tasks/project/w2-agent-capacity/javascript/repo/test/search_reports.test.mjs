import test from 'node:test';
import assert from 'node:assert/strict';
import { Helpdesk } from '../src/index.mjs';

function setup() {
  const hd = new Helpdesk();
  hd.addAgent('ana');
  hd.addRequester('zoe');
  hd.tickets.create('VPN drops', 'zoe', 'high', ['vpn']);
  const b = hd.tickets.create('Printer jammed', 'zoe', 'low');
  hd.tickets.changeStatus(b.id, 'open');
  return hd;
}

test('search', () => {
  const hd = setup();
  const ids = (q) => hd.search(q).map((t) => t.id);
  assert.deepEqual(ids('status:open'), [2]);
  assert.deepEqual(ids('tag:vpn'), [1]);
  assert.deepEqual(ids('-status:open printer'), []);
  assert.deepEqual(ids('printer'), [2]);
});

test('overdue and summary', () => {
  const hd = setup();
  hd.clock.set(1000);
  assert.deepEqual(hd.overdue().map((t) => t.id), [1]);
  const s = hd.summary();
  assert.equal(s.status.open, 1);
  assert.deepEqual(s.assignee, { unassigned: 2 });
});

test('csv', () => {
  const hd = setup();
  assert.ok(hd.exportCsv().startsWith('id,title,requester'));
  const made = hd.importCsv('title,requester,tags\nBroken mouse,zoe,usb;hw\n');
  assert.deepEqual([made[0].title, made[0].tags], ['Broken mouse', ['hw', 'usb']]);
});
