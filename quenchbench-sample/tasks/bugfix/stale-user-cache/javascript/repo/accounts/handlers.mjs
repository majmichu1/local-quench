// Request handlers used by the admin panel. They only translate between objects and the service.
import { NotFound } from './models.mjs';

const view = (u) => ({ id: u.id, email: u.email, name: u.name, team: u.team });

export function handle(service, req) {
  try {
    switch (req.action) {
      case 'get': return { ok: true, user: view(service.getUser(req.id)) };
      case 'lookup': return { ok: true, user: view(service.getByEmail(req.email)) };
      case 'team': return { ok: true, members: service.teamMembers(req.team) };
      case 'rename': return { ok: true, user: view(service.rename(req.id, req.name)) };
      case 'email': return { ok: true, user: view(service.changeEmail(req.id, req.email)) };
      case 'move': return { ok: true, user: view(service.moveTeam(req.id, req.team)) };
      case 'delete': service.deleteUser(req.id); return { ok: true };
      default: return { ok: false, error: `unknown action ${JSON.stringify(req.action)}` };
    }
  } catch (err) {
    if (err instanceof NotFound || err instanceof Error) return { ok: false, error: err.message };
    throw err;
  }
}
