import { flush, log } from './lib/log.mjs';
import { loadUser } from './lib/users.mjs';

log('start');
setTimeout(() => log('timeout'), 0);
loadUser(1).then((u) => log(`user ${u.name}`));
queueMicrotask(() => log('microtask'));
(async () => {
  log('async-begin');
  await null;
  log('async-after-await');
})();
log('end');
setTimeout(flush, 20);
