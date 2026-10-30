import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { splitRow } from './rows.mjs';

test('cases', () => {
  assert.deepEqual(splitRow('a,b,c'), ['a', 'b', 'c']);
  assert.deepEqual(splitRow('a,"b,c",d'), ['a', 'b,c', 'd']);
  assert.deepEqual(splitRow('"say ""hi""",x'), ['say "hi"', 'x']);
  assert.deepEqual(splitRow('a,,b'), ['a', '', 'b']);
  assert.deepEqual(splitRow(''), ['']);
  assert.deepEqual(splitRow('a,'), ['a', '']);
});

test('no library', () => {
  assert.ok(!/from ['"]csv/.test(readFileSync(new URL('./rows.mjs', import.meta.url), 'utf8')));
});
