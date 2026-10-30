export class LRUCache {
  constructor(capacity, { onEvict } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new RangeError('capacity must be a positive integer');
    this.capacity = capacity;
    this.onEvict = onEvict;
    this.map = new Map();
    this.order = []; // least recently used first
  }

  touch(key) {
    const i = this.order.indexOf(key);
    if (i >= 0) this.order.splice(i, 1);
    this.order.push(key);
  }

  get(key) {
    if (!this.map.has(key)) return undefined;
    this.touch(key);
    return this.map.get(key);
  }

  set(key, value) {
    this.map.set(key, value);
    this.touch(key);
    if (this.map.size > this.capacity) {
      const old = this.order.shift();
      const v = this.map.get(old);
      this.map.delete(old);
      if (this.onEvict) this.onEvict(old, v);
    }
    return this;
  }

  has(key) {
    return this.map.has(key);
  }

  delete(key) {
    if (!this.map.has(key)) return false;
    this.map.delete(key);
    this.order.splice(this.order.indexOf(key), 1);
    return true;
  }

  get size() {
    return this.map.size;
  }

  keys() {
    return [...this.order];
  }
}
