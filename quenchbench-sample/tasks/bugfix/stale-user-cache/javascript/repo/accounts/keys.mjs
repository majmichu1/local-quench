// Cache key helpers, so every layer spells keys the same way.
export const userKey = (id) => `user:${id}`;
export const emailKey = (email) => `email:${email}`;
export const teamKey = (team) => `team:${team}`;
