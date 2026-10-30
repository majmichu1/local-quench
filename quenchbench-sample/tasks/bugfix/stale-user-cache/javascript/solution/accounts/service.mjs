// User service: reads go through the cache, writes go to the repository.
import { emailKey, teamKey, userKey } from './keys.mjs';
import { copyUser } from './models.mjs';

export class UserService {
  constructor(repo, cache) {
    this.repo = repo;
    this.cache = cache;
  }

  // ------------------------------------------------------------------ reads
  // The cache keeps its own copies: callers get a fresh copy, so changing a returned user
  // (or a write that fails half way) never changes what is cached.
  getUser(id) {
    let user = this.cache.get(userKey(id));
    if (user === undefined) {
      user = this.repo.get(id);
      this.cache.set(userKey(id), copyUser(user));
    }
    return copyUser(user);
  }

  getByEmail(email) {
    let user = this.cache.get(emailKey(email));
    if (user === undefined) {
      user = this.repo.findByEmail(email);
      this.cache.set(emailKey(email), copyUser(user));
    }
    return copyUser(user);
  }

  teamMembers(team) {
    let names = this.cache.get(teamKey(team));
    if (names === undefined) {
      names = this.repo.listTeam(team).map((u) => u.name);
      this.cache.set(teamKey(team), [...names]);
    }
    return [...names];
  }

  // ----------------------------------------------------------------- writes
  // Drop every cached entry that may contain one of these user states (old and new).
  invalidate(...users) {
    const keys = new Set();
    for (const u of users) {
      keys.add(userKey(u.id));
      keys.add(emailKey(u.email));
      keys.add(teamKey(u.team));
    }
    this.cache.delete(...keys);
  }

  update(id, changes) {
    const old = this.getUser(id);
    const next = { ...old, ...changes };
    this.repo.save(next); // may throw: nothing has been changed yet
    this.invalidate(old, next);
    return copyUser(next);
  }

  rename(id, name) {
    return this.update(id, { name });
  }

  changeEmail(id, email) {
    return this.update(id, { email });
  }

  moveTeam(id, team) {
    return this.update(id, { team });
  }

  deleteUser(id) {
    const old = this.repo.get(id);
    this.repo.delete(id);
    this.invalidate(old);
  }
}
