// Tiny demo: node cli.mjs prints a report for a few sample tickets.
import { Helpdesk } from './src/index.mjs';

const hd = new Helpdesk();
hd.addAgent('ana', ['network']);
hd.addAgent('ben');
hd.addRequester('zoe');
for (const [title, prio, tags] of [['VPN drops every hour', 'high', ['vpn']], ['Printer jammed', 'low', []],
  ['Cannot log in', 'urgent', ['sso']]]) {
  const t = hd.tickets.create(title, 'zoe', prio, tags);
  hd.tickets.autoAssign(t.id);
}
console.log(hd.report());
