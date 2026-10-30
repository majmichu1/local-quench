import test from 'node:test';
import assert from 'node:assert/strict';
import { Cache } from './accounts/cache.mjs';
import { NotFound, makeUser } from './accounts/models.mjs';
import { UserRepository } from './accounts/repository.mjs';
import { UserService } from './accounts/service.mjs';

function make() {
  const repo = new UserRepository([
    makeUser(1, 'ann@x.io', 'Ann', 'red'),
    makeUser(2, 'bob@x.io', 'Bob', 'red'),
    makeUser(3, 'cid@x.io', 'Cid', 'blue'),
  ]);
  return { repo, svc: new UserService(repo, new Cache()) };
}

function warm(svc) {
  for (const [id, email] of [[1, 'ann@x.io'], [2, 'bob@x.io'], [3, 'cid@x.io']]) {
    svc.getUser(id);
    svc.getByEmail(email);
  }
  svc.teamMembers('red');
  svc.teamMembers('blue');
}

test('reads are cached', () => {
  const { repo, svc } = make();
  assert.equal(svc.getUser(1).name, 'Ann');
  assert.equal(svc.getByEmail('bob@x.io').id, 2);
  assert.deepEqual(svc.teamMembers('red'), ['Ann', 'Bob']);
  const q = repo.queries;
  assert.equal(svc.getUser(1).name, 'Ann');
  assert.equal(svc.getByEmail('bob@x.io').id, 2);
  assert.deepEqual(svc.teamMembers('red'), ['Ann', 'Bob']);
  assert.equal(repo.queries, q);
});

test('rename', () => {
  const { svc } = make();
  warm(svc);
  assert.equal(svc.rename(1, 'Anna').name, 'Anna');
  assert.equal(svc.getUser(1).name, 'Anna');
  assert.equal(svc.getByEmail('ann@x.io').name, 'Anna');
  assert.deepEqual(svc.teamMembers('red'), ['Anna', 'Bob']);
});

test('change email', () => {
  const { svc } = make();
  warm(svc);
  svc.changeEmail(1, 'anna@x.io');
  assert.throws(() => svc.getByEmail('ann@x.io'), NotFound);
  assert.equal(svc.getByEmail('anna@x.io').id, 1);
  assert.equal(svc.getUser(1).email, 'anna@x.io');
});

test('rejected email change leaves no trace', () => {
  const { repo, svc } = make();
  warm(svc);
  assert.throws(() => svc.changeEmail(1, 'bob@x.io'), /email taken/);
  assert.equal(svc.getUser(1).email, 'ann@x.io');
  assert.equal(svc.getByEmail('ann@x.io').id, 1);
  assert.equal(svc.getByEmail('bob@x.io').id, 2);
  assert.equal(repo.get(1).email, 'ann@x.io');
});

test('move team', () => {
  const { svc } = make();
  warm(svc);
  assert.equal(svc.moveTeam(2, 'blue').team, 'blue');
  assert.deepEqual(svc.teamMembers('red'), ['Ann']);
  assert.deepEqual(svc.teamMembers('blue'), ['Bob', 'Cid']);
  assert.equal(svc.getUser(2).team, 'blue');
  assert.equal(svc.getByEmail('bob@x.io').team, 'blue');
});

test('delete', () => {
  const { svc } = make();
  warm(svc);
  svc.deleteUser(2);
  assert.throws(() => svc.getUser(2), NotFound);
  assert.throws(() => svc.getByEmail('bob@x.io'), NotFound);
  assert.deepEqual(svc.teamMembers('red'), ['Ann']);
});

test('returned objects are not shared with the cache', () => {
  const { svc } = make();
  const u = svc.getUser(1);
  u.name = 'ANN';
  assert.equal(svc.getUser(1).name, 'Ann');
  const v = svc.getByEmail('cid@x.io');
  v.team = 'zzz';
  assert.equal(svc.getByEmail('cid@x.io').team, 'blue');
  const m = svc.teamMembers('red');
  m.push('Mallory');
  assert.deepEqual(svc.teamMembers('red'), ['Ann', 'Bob']);
});

test('writes keep unrelated entries cached', () => {
  const { repo, svc } = make();
  warm(svc);
  svc.rename(1, 'Anna');
  svc.changeEmail(2, 'robert@x.io');
  const q = repo.queries;
  assert.equal(svc.getUser(3).name, 'Cid');
  assert.equal(svc.getByEmail('cid@x.io').id, 3);
  assert.deepEqual(svc.teamMembers('blue'), ['Cid']);
  assert.equal(repo.queries, q);
});
