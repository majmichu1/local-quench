import { LRUCache } from './cache.mjs';

// Memoize fn on its (JSON-serialisable) arguments, keeping the `capacity` most recent results.
export function memoize(fn, capacity = 1000) {
  const cache = new LRUCache(capacity);
  const wrapped = (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const value = fn(...args);
    cache.set(key, value);
    return value;
  };
  wrapped.cache = cache;
  return wrapped;
}
