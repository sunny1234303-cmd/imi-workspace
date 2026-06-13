const { getAuthClient } = require('../_lib/google');

module.exports = async (req, res) => {
  try {
    const auth = await getAuthClient(req, res);
    res.json({ authenticated: !!auth });
  } catch {
    res.json({ authenticated: false });
  }
};
