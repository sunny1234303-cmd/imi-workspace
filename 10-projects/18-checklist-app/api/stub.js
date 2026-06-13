const RESPONSES = {
  sync:           () => ({ ok: true, files: [] }),
  'sync-files':   () => ({ files: [] }),
  'sync-memo':    () => ({ ok: false, reason: 'Apple Notes requires macOS desktop app' }),
  todos:          (method) => method === 'GET' ? { todos: [] } : { ok: true },
  log:            (method) => method === 'GET' ? [] : { ok: true },
  history:        () => ({}),
  'create-group': () => ({ ok: true }),
  'delete-group': () => ({ ok: true }),
};

module.exports = (req, res) => {
  const route = req.query.route;
  const handler = RESPONSES[route];
  if (!handler) return res.status(404).json({ error: 'Not found' });
  res.json(handler(req.method));
};
