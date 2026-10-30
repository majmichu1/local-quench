// A small key/value cache with optional expiry.
export class Cache {
  constructor({ ttlMs = 300000, clock = () => Date.now() } = {}) {
    this.ttlMs = ttlMs;
    this.clock = clock;
    this.data = new Map();
  }

  get(key) {
    const entry = this.data.get(key);
    if (!entry) return undefined;
    if (this.clock() >= entry.expires) {
      this.data.delete(key);
      return undefined;
    }
    return entry.value;
  }

  set(key, value) {
    this.data.set(key, { value, expires: this.clock() + this.ttlMs });
  }

  delete(...keys) {
    for (const k of keys) this.data.delete(k);
  }

  clear() {
    this.data.clear();
  }

  get size() {
    return this.data.size;
  }
}
