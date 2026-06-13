const redis = require('./_lib/redis');
const { getAuthClient, getUserId } = require('./_lib/google');

const MAX_LOG = 200;

module.exports = async (req, res) => {
  const type = req.query.type;

  try {
    const auth = await getAuthClient(req, res);
    if (!auth) return res.status(401).json({ error: 'Not authenticated' });

    const uid = await getUserId(req, auth);
    if (!uid) return res.status(401).json({ error: 'Cannot identify user' });

    // ── todos ──────────────────────────────────────────────
    if (type === 'todos') {
      if (req.method === 'GET') {
        const todos = await redis.get(`u:${uid}:todos`) || [];
        return res.json({ todos });
      }
      if (req.method === 'POST') {
        await redis.set(`u:${uid}:todos`, req.body.todos || []);
        return res.json({ ok: true });
      }
    }

    // ── sync (companies + todos) ────────────────────────────
    if (type === 'sync') {
      if (req.method === 'POST') {
        const { todos, companies } = req.body;
        await Promise.all([
          todos     && redis.set(`u:${uid}:todos`,     todos),
          companies && redis.set(`u:${uid}:companies`, companies),
        ].filter(Boolean));
        return res.json({ ok: true, files: [] });
      }
    }

    // ── log ────────────────────────────────────────────────
    if (type === 'log') {
      const key = `u:${uid}:log`;
      if (req.method === 'GET') {
        const log = await redis.get(key) || [];
        return res.json(log);
      }
      if (req.method === 'POST') {
        const now = new Date();
        const ts  = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
        const entry = { type: req.body.type, data: req.body.data, ts };
        const log   = await redis.get(key) || [];
        log.unshift(entry);
        await redis.set(key, log.slice(0, MAX_LOG));
        return res.json({ ok: true });
      }
    }

    res.status(400).json({ error: 'Unknown type' });
  } catch (e) {
    console.error('[data]', e.message);
    res.status(500).json({ error: e.message });
  }
};
