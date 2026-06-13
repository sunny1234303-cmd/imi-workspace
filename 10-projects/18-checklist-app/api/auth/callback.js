const { getOAuth2Client, setCookies } = require('../_lib/google');

module.exports = async (req, res) => {
  const { code, error } = req.query;

  if (error || !code) {
    return res.send(`<script>window.opener?.postMessage('gcal_error','*');window.close();</script>`);
  }

  try {
    const oauth2 = getOAuth2Client();
    const { tokens } = await oauth2.getToken(code);
    setCookies(res, tokens);
    res.send(`<script>window.opener?.postMessage('gcal_ok','*');window.close();</script>`);
  } catch (e) {
    console.error('[callback]', e.message);
    res.send(`<script>window.opener?.postMessage('gcal_error','*');window.close();</script>`);
  }
};
