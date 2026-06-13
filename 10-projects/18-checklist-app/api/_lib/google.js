const { google } = require('googleapis');

function getOAuth2Client() {
  return new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
  );
}

function parseCookies(req) {
  const raw = req.headers.cookie || '';
  const out = {};
  raw.split(';').forEach(pair => {
    const idx = pair.indexOf('=');
    if (idx < 0) return;
    const key = pair.slice(0, idx).trim();
    const val = pair.slice(idx + 1).trim();
    try { out[key] = decodeURIComponent(val); } catch { out[key] = val; }
  });
  return out;
}

function setCookies(res, tokens) {
  const opts = 'HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=31536000';
  const cookies = [];
  if (tokens.access_token)  cookies.push(`g_at=${encodeURIComponent(tokens.access_token)}; ${opts}`);
  if (tokens.refresh_token) cookies.push(`g_rt=${encodeURIComponent(tokens.refresh_token)}; ${opts}`);
  if (tokens.expiry_date)   cookies.push(`g_exp=${tokens.expiry_date}; ${opts}`);
  if (cookies.length) res.setHeader('Set-Cookie', cookies);
}

async function getAuthClient(req, res) {
  const cookies     = parseCookies(req);
  const accessToken = cookies.g_at;
  const refreshToken = cookies.g_rt;
  const expiry      = parseInt(cookies.g_exp || '0');

  if (!accessToken && !refreshToken) return null;

  const oauth2 = getOAuth2Client();
  oauth2.setCredentials({ access_token: accessToken, refresh_token: refreshToken, expiry_date: expiry });

  if (expiry && Date.now() > expiry - 60000) {
    try {
      const { credentials } = await oauth2.refreshAccessToken();
      oauth2.setCredentials(credentials);
      setCookies(res, credentials);
    } catch {
      return null;
    }
  }

  return oauth2;
}

module.exports = { getOAuth2Client, parseCookies, setCookies, getAuthClient };
