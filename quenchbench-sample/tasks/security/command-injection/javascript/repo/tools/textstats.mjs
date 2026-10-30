import { execSync } from 'node:child_process';

const opts = { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] };

// Number of lines in the file at path (wc -l).
export function countLines(path) {
  const out = execSync(`wc -l ${path}`, opts);
  return parseInt(out.trim().split(/\s+/)[0], 10);
}

// Number of lines of path containing pattern literally (grep -c -F).
export function countMatches(pattern, path) {
  try {
    return parseInt(execSync(`grep -c -F '${pattern}' ${path}`, opts).trim(), 10);
  } catch (e) {
    if (e.status === 1) return 0;
    throw new Error(`grep failed: ${e.stderr}`);
  }
}
