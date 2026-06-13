const { google } = require('googleapis');
const { getOAuth2Client } = require('../_lib/google');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { action, code, refresh_token } = req.body;

  try {
    const oauth2 = getOAuth2Client();

    if (action === 'exchange') {
      console.log('[token/exchange] step1: getting token, code prefix:', code?.slice(0, 10));
      let tokens;
      try {
        const result = await oauth2.getToken(code);
        tokens = result.tokens;
        console.log('[token/exchange] step1 ok, has access_token:', !!tokens.access_token);
      } catch (e) {
        console.error('[token/exchange] step1 FAILED:', e.message);
        return res.status(500).json({ error: 'code_exchange_failed: ' + e.message });
      }

      oauth2.setCredentials(tokens);

      let userInfo = { id: null, email: null };
      try {
        const oauth2api = google.oauth2({ version: 'v2', auth: oauth2 });
        const { data } = await oauth2api.userinfo.get();
        userInfo = data;
        console.log('[token/exchange] step2 ok, email:', userInfo.email);
      } catch (e) {
        console.error('[token/exchange] step2 (userinfo) FAILED:', e.message);
        // userinfo 실패해도 access_token이 있으면 계속 진행
      }

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
