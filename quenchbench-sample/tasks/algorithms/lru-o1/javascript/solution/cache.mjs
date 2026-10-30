// Map from key to a node of a doubly linked list ordered from least (head) to most (tail) recently used.
export class LRUCache {
  constructor(capacity, { onEvict } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new RangeError('capacity must be a positive integer');
    this.capacity = capacity;
    this.onEvict = onEvict;
    this.map = new Map();
    this.head = null;
    this.tail = null;
  }

  unlink(node) {
    if (node.prev) node.prev.next = node.next;
    else this.head = node.next;
    if (node.next) node.next.prev = node.prev;
    else this.tail = node.prev;
    node.prev = node.next = null;
  }

  append(node) {
    node.prev = this.tail;
    node.next = null;
    if (this.tail) this.tail.next = node;
    else this.head = node;
    this.tail = node;
  }

  get(key) {
    const node = this.map.get(key);
    if (node === undefined) return undefined;
    if (node !== this.tail) {
      this.unlink(node);
      this.append(node);
    }
    return node.value;
  }

  set(key, value) {
    let node = this.map.get(key);
    if (node !== undefined) {
      node.value = value;
      if (node !== this.tail) {
        this.unlink(node);
        this.append(node);
      }
      return this;
    }
    node = { key, value, prev: null, next: null };
    this.map.set(key, node);
    this.append(node);
    if (this.map.size > this.capacity) {
      const old = this.head;
      this.unlink(old);
      this.map.delete(old.key);
      if (this.onEvict) this.onEvict(old.key, old.value);
    }
    return this;
  }

  has(key) {
    return this.map.has(key);
  }

  delete(key) {
    const node = this.map.get(key);
    if (node === undefined) return false;
    this.unlink(node);
    this.map.delete(key);
    return true;
  }

  get size() {
    return this.map.size;
  }

  keys() {
    const out = [];
    for (let n = this.head; n; n = n.next) out.push(n.key);
    return out;
  }
}
