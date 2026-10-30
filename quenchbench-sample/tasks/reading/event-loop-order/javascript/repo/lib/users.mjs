const cache = new Map([[1, { name: 'ana' }]]);

async function fetchCached(id) {
  return cache.get(id);
}

export async function loadUser(id) {
  if (!cache.has(id)) throw new Error(`unknown user ${id}`);
  return fetchCached(id);
}
