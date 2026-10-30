// In-memory stand-in for the users table. Every read counts as one query.
import { NotFound, copyUser } from './models.mjs';

export class UserRepository {
  constructor(users = []) {
    this.rows = new Map();
    this.queries = 0;
    for (const u of users) this.rows.set(u.id, copyUser(u));
  }

  get(id) {
    this.queries++;
    const row = this.rows.get(id);
    if (!row) throw new NotFound(`user ${id} not found`);
    return copyUser(row);
  }

  findByEmail(email) {
    this.queries++;
    for (const row of this.rows.values()) {
      if (row.email === email) return copyUser(row);
    }
    throw new NotFound(`no user with email ${email}`);
  }

  listTeam(team) {
    this.queries++;
    return [...this.rows.values()]
      .filter((r) => r.team === team)
      .sort((a, b) => a.id - b.id)
      .map(copyUser);
  }

  save(user) {
    for (const row of this.rows.values()) {
      if (row.id !== user.id && row.email === user.email) throw new Error(`email taken: ${user.email}`);
    }
    if (!this.rows.has(user.id)) throw new NotFound(`user ${user.id} not found`);
    this.rows.set(user.id, copyUser(user));
  }

  delete(id) {
    if (!this.rows.delete(id)) throw new NotFound(`user ${id} not found`);
  }
}
