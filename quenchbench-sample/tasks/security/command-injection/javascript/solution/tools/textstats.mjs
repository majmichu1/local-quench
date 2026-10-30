import { execFileSync } from 'node:child_process';

const opts = { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] };

// Number of lines in the file at path (wc -l).
export function countLines(path) {
  let out;
  try {
    out = execFileSync('wc', ['-l', '--', path], opts);
  } catch (e) {
    throw new Error(`wc failed: ${e.stderr}`);
  }
  return parseInt(out.trim().split(/\s+/)[0], 10);
}

// Number of lines of path containing pattern literally (grep -c -F).
export function countMatches(pattern, path) {
  try {
    return parseInt(execFileSync('grep', ['-c', '-F', '-e', pattern, '--', path], opts).trim(), 10);
  } catch (e) {
    if (e.status === 1) return 0;
    throw new Error(`grep failed: ${e.stderr}`);
  }
}
