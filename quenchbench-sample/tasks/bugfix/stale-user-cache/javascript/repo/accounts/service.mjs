// User service: reads go through the cache, writes go to the repository.
import { emailKey, teamKey, userKey } from './keys.mjs';

export class UserService {
  constructor(repo, cache) {
    this.repo = repo;
    this.cache = cache;
  }

  // ------------------------------------------------------------------ reads
  getUser(id) {
    let user = this.cache.get(userKey(id));
    if (user === undefined) {
      user = this.repo.get(id);
      this.cache.set(userKey(id), user);
    }
    return user;
  }

  getByEmail(email) {
    let user = this.cache.get(emailKey(email));
    if (user === undefined) {
      user = this.repo.findByEmail(email);
      this.cache.set(emailKey(email), user);
    }
    return user;
  }

  teamMembers(team) {
    let names = this.cache.get(teamKey(team));
    if (names === undefined) {
      names = this.repo.listTeam(team).map((u) => u.name);
      this.cache.set(teamKey(team), names);
    }
    return [...names];
  }

  // ----------------------------------------------------------------- writes
  rename(id, name) {
    const user = this.getUser(id);
    user.name = name;
    this.repo.save(user);
    this.cache.delete(userKey(id), teamKey(user.team));
    return user;
  }

  changeEmail(id, email) {
    const user = this.getUser(id);
    user.email = email;
    this.repo.save(user);
    this.cache.delete(userKey(id));
    return user;
  }

  moveTeam(id, team) {
    const user = this.getUser(id);
    user.team = team;
    this.repo.save(user);
    this.cache.delete(userKey(id), teamKey(team));
    return user;
  }

  deleteUser(id) {
    this.repo.delete(id);
    this.cache.delete(userKey(id));
  }
}
