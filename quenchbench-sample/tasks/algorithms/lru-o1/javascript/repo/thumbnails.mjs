import { LRUCache } from './cache.mjs';

const cache = new LRUCache(5000);

export function thumbnail(id, render) {
  let t = cache.get(id);
  if (t === undefined) {
    t = render(id);
    cache.set(id, t);
  }
  return t;
}
