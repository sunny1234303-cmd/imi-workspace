const { google } = require('googleapis');
const { getOAuth2Client, setCookies } = require('../_lib/google');

module.exports = async (req, res) => {
  const { code, error } = req.query;

  if (error || !code) {
    return res.send(`<script>window.opener?.postMessage('gcal_error','*');window.close();</script>`);
  }

  try {
    const oauth2 = getOAuth2Client();
    const { tokens } = await oauth2.getToken(code);
    oauth2.setCredentials(tokens);

    // 사용자 ID 조회 (KV 키 + 쿠키 저장용)
    const oauth2api = google.oauth2({ version: 'v2', auth: oauth2 });
    const { data: userInfo } = await oauth2api.userinfo.get();

    setCookies(res, tokens, userInfo.id);
    res.send(`<script>window.opener?.postMessage('gcal_ok','*');window.close();</script>`);
  } catch (e) {
    console.error('[callback]', e.message);
    res.send(`<script>window.opener?.postMessage('gcal_error','*');window.close();</script>`);
  }
};
