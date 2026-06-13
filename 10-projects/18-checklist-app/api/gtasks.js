const { google } = require('googleapis');
const { getAuthClient } = require('./_lib/google');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const auth = await getAuthClient(req, res);
    if (!auth) return res.status(401).json({ error: 'Not authenticated' });

    const tasks = google.tasks({ version: 'v1', auth });
    const { title, notes } = req.body;

    const { data: lists } = await tasks.tasklists.list({ maxResults: 1 });
    const listId = lists.items?.[0]?.id || '@default';

    const { data } = await tasks.tasks.insert({
      tasklist: listId,
      requestBody: {
        title: title || '',
        notes: notes || '',
      },
    });

    res.json({ ok: true, id: data.id });
  } catch (e) {
    console.error('[gtasks]', e.message);
    res.status(500).json({ error: e.message });
  }
};
