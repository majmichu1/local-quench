export class NotFound extends Error {
  constructor(message) {
    super(message);
    this.name = 'NotFound';
  }
}

/** A user row: { id, email, name, team }. */
export function makeUser(id, email, name, team) {
  return { id, email, name, team };
}

export function copyUser(u) {
  return { id: u.id, email: u.email, name: u.name, team: u.team };
}
