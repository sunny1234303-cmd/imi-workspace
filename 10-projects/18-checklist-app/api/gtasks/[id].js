const { google } = require('googleapis');
const { getAuthClient } = require('../_lib/google');

module.exports = async (req, res) => {
  if (req.method !== 'DELETE') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const auth = await getAuthClient(req, res);
    if (!auth) return res.status(401).json({ error: 'Not authenticated' });

    const tasks = google.tasks({ version: 'v1', auth });
    const { id } = req.query;

    const { data: lists } = await tasks.tasklists.list({ maxResults: 1 });
    const listId = lists.items?.[0]?.id || '@default';

    await tasks.tasks.delete({ tasklist: listId, task: id });
    res.json({ ok: true });
  } catch (e) {
    console.error('[gtasks/[id]]', e.message);
    res.status(500).json({ error: e.message });
  }
};
