const lines = [];

export function log(msg) {
  lines.push(msg);
}

export function flush() {
  console.log(lines.join('\n'));
}
