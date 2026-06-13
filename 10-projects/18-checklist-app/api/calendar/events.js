const { google } = require('googleapis');
const { getAuthClient } = require('../_lib/google');

module.exports = async (req, res) => {
  try {
    const auth = await getAuthClient(req, res);
    if (!auth) return res.status(401).json({ error: 'Not authenticated' });

    const calendar = google.calendar({ version: 'v3', auth });

    if (req.method === 'GET') {
      const { year, month } = req.query;
      const y = parseInt(year);
      const m = parseInt(month) - 1;
      const timeMin = new Date(y, m, 1).toISOString();
      const timeMax = new Date(y, m + 1, 0, 23, 59, 59).toISOString();

      const { data } = await calendar.events.list({
        calendarId: 'primary',
        timeMin,
        timeMax,
        singleEvents: true,
        orderBy: 'startTime',
        maxResults: 250,
      });

      return res.json({ events: data.items || [] });
    }

    if (req.method === 'POST') {
      const { title, date, description } = req.body;

      const { data } = await calendar.events.insert({
        calendarId: 'primary',
        requestBody: {
          summary: title,
          description: description || '',
          start: { date },
          end: { date },
        },
      });

      return res.json({ ok: true, id: data.id });
    }

    res.status(405).json({ error: 'Method not allowed' });
  } catch (e) {
    console.error('[calendar/events]', e.message);
    res.status(500).json({ error: e.message });
  }
};
