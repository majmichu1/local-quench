import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { countLines, countMatches } from './tools/textstats.mjs';
import { summarize } from './report.mjs';

const dir = mkdtempSync(join(tmpdir(), 'cmdinj-'));
process.chdir(dir);
writeFileSync('data.txt', 'TODO one\ntwo\nTODO three\n');
writeFileSync('my notes.txt', "a\nb it's\n");
writeFileSync('-n.txt', 'x\ny\nz\nw\n');
writeFileSync('$(touch PWNED3).txt', 'q\n');
const pwned = () => readdirSync(dir).filter((f) => f.startsWith('PWNED') && !f.endsWith('.txt'));

test('normal', () => {
  assert.equal(countLines('data.txt'), 3);
  assert.equal(countMatches('TODO', 'data.txt'), 2);
  assert.equal(countMatches('nothing', 'data.txt'), 0);
  assert.deepEqual(summarize(['data.txt']), { 'data.txt': [3, 2] });
});

test('odd names', () => {
  assert.equal(countLines('my notes.txt'), 2);
  assert.equal(countLines(join(dir, 'my notes.txt')), 2);
  assert.equal(countLines('-n.txt'), 4);
  assert.equal(countLines('$(touch PWNED3).txt'), 1);
  assert.equal(countMatches("it's", 'my notes.txt'), 1);
  assert.equal(countMatches('-v', '-n.txt'), 0);
  assert.deepEqual(pwned(), []);
});

test('injection blocked', () => {
  for (const bad of ['data.txt; touch PWNED1', 'data.txt && touch PWNED2', '$(touch PWNED4)', '`touch PWNED5`',
    'nope.txt | touch PWNED6']) {
    assert.throws(() => countLines(bad), Error, bad);
  }
  assert.equal(countMatches("x'; touch PWNED7; echo '", 'data.txt'), 0);
  assert.throws(() => countMatches('TODO', 'data.txt; touch PWNED8'));
  assert.deepEqual(pwned(), []);
});

test('missing file', () => {
  assert.throws(() => countLines('missing.txt'));
  assert.throws(() => countMatches('a', 'missing.txt'));
});
