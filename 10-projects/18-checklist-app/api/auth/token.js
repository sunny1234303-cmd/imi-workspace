const { google } = require('googleapis');
const { getOAuth2Client } = require('../_lib/google');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { action, code, refresh_token } = req.body;

  try {
    const oauth2 = getOAuth2Client();

    if (action === 'exchange') {
      const { tokens } = await oauth2.getToken(code);
      oauth2.setCredentials(tokens);

      const oauth2api = google.oauth2({ version: 'v2', auth: oauth2 });
      const { data: userInfo } = await oauth2api.userinfo.get();

      return res.json({
        access_token:  tokens.access_token,
        refresh_token: tokens.refresh_token,
        expiry_date:   tokens.expiry_date,
        user_id:       userInfo.id,
        email:         userInfo.email,
      });
    }

    if (action === 'refresh') {
      oauth2.setCredentials({ refresh_token });
      const { credentials } = await oauth2.refreshAccessToken();
      return res.json({
        access_token: credentials.access_token,
        expiry_date:  credentials.expiry_date,
      });
    }

    res.status(400).json({ error: 'Invalid action' });
  } catch (e) {
    console.error('[auth/token]', e.message);
    res.status(500).json({ error: e.message });
  }
};
