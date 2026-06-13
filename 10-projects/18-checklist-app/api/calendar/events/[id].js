const { google } = require('googleapis');
const { getAuthClient } = require('../../_lib/google');

module.exports = async (req, res) => {
  if (req.method !== 'DELETE') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const auth = await getAuthClient(req, res);
    if (!auth) return res.status(401).json({ error: 'Not authenticated' });

    const calendar = google.calendar({ version: 'v3', auth });
    const { id } = req.query;

    await calendar.events.delete({ calendarId: 'primary', eventId: id });
    res.json({ ok: true });
  } catch (e) {
    console.error('[calendar/events/[id]]', e.message);
    res.status(500).json({ error: e.message });
  }
};
