const { app, BrowserWindow, screen, ipcMain, shell, safeStorage } = require('electron');
const path    = require('path');
const { execSync } = require('child_process');
const fs      = require('fs');
const https   = require('https');

const API_BASE    = 'https://18-checklist-app.vercel.app';
const CALLBACK_URL = `${API_BASE}/api/auth/callback`;
const TOKEN_FILE  = () => path.join(app.getPath('userData'), 'gtoken.bin');

// ── 단일 인스턴스 ─────────────────────────────────────────────
if (!app.requestSingleInstanceLock()) { app.quit(); process.exit(0); }

let floatWin = null;
let mainWin  = null;
let lastOpenedDate = null;

app.on('second-instance', () => {
  if (mainWin) { mainWin.show(); mainWin.focus(); }
  else if (floatWin) { floatWin.show(); floatWin.focus(); }
});

// ── 토큰 저장/로드 ────────────────────────────────────────────
function saveToken(data) {
  const json = JSON.stringify(data);
  const buf  = safeStorage.isEncryptionAvailable()
    ? safeStorage.encryptString(json)
    : Buffer.from(json, 'utf-8');
  fs.writeFileSync(TOKEN_FILE(), buf);
}

function loadToken() {
  try {
    const file = TOKEN_FILE();
    if (!fs.existsSync(file)) return null;
    const buf  = fs.readFileSync(file);
    const json = safeStorage.isEncryptionAvailable()
      ? safeStorage.decryptString(buf)
      : buf.toString('utf-8');
    return JSON.parse(json);
  } catch { return null; }
}

function clearToken() {
  try { fs.unlinkSync(TOKEN_FILE()); } catch {}
}

// ── 토큰 갱신 ─────────────────────────────────────────────────
async function fetchJson(url, options = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const body = options.body ? Buffer.from(options.body, 'utf-8') : null;
    const req  = https.request({
      hostname: u.hostname,
      path: u.pathname + u.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(body ? { 'Content-Length': body.length } : {}),
        ...(options.headers || {}),
      },
    }, res => {
      let data = '';
      res.on('data', c => { data += c; });
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch(e) { reject(e); } });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getValidToken() {
  let token = loadToken();
  if (!token) return null;

  const now = Date.now();
  if (token.expiry_date && now > token.expiry_date - 60000) {
    try {
      const refreshed = await fetchJson(`${API_BASE}/api/auth/token`, {
        method: 'POST',
        body: JSON.stringify({ action: 'refresh', refresh_token: token.refresh_token }),
      });
      token = { ...token, access_token: refreshed.access_token, expiry_date: refreshed.expiry_date };
      saveToken(token);
    } catch { return null; }
  }
  return token;
}

// ── OAuth 팝업 ────────────────────────────────────────────────
function openAuthWindow() {
  const authWin = new BrowserWindow({
    width: 520,
    height: 640,
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  });

  authWin.loadURL(`${API_BASE}/api/auth/google`);

  const handleRedirect = async (url) => {
    if (!url.startsWith(CALLBACK_URL)) return false;

    const urlObj  = new URL(url);
    const code    = urlObj.searchParams.get('code');
    const errParam = urlObj.searchParams.get('error');

    authWin.destroy();

    if (errParam || !code) {
      mainWin?.webContents.send('auth-result', { ok: false });
      return true;
    }

    try {
      const data = await fetchJson(`${API_BASE}/api/auth/token`, {
        method: 'POST',
        body: JSON.stringify({ action: 'exchange', code }),
      });
      saveToken(data);
      mainWin?.webContents.send('auth-result', { ok: true, email: data.email });
    } catch (e) {
      mainWin?.webContents.send('auth-result', { ok: false, error: e.message });
    }
    return true;
  };

  authWin.webContents.on('will-redirect', (event, url) => {
    if (url.startsWith(CALLBACK_URL)) { event.preventDefault(); handleRedirect(url); }
  });
  authWin.webContents.on('did-navigate', (_, url) => { handleRedirect(url); });
}

// ── 플로팅 버튼 창 ────────────────────────────────────────────
function createFloatWindow() {
  floatWin = new BrowserWindow({
    width: 96, height: 48,
    frame: false, transparent: true, alwaysOnTop: true,
    resizable: false, hasShadow: false, skipTaskbar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });
  const { width } = screen.getPrimaryDisplay().workAreaSize;
  floatWin.setPosition(width - 116, 16);
  floatWin.loadFile(path.join(__dirname, 'float/index.html'));
  floatWin.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: false });
  floatWin.setAlwaysOnTop(true, 'floating');
  floatWin.on('closed', () => { floatWin = null; });
}

function todayStr() { return new Date().toISOString().slice(0, 10); }

const WIN_W = 440, WIN_H = 720;

function calcMainPos(fx, fy) {
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const isLeft = fx < sw / 2;
  const winX = isLeft ? Math.max(0, fx) : Math.min(fx + 96 - WIN_W, sw - WIN_W);
  const winY = Math.min(fy + 48 + 8, sh - WIN_H - 8);
  return [Math.round(winX), Math.round(winY)];
}

// ── 메인 체크리스트 창 ────────────────────────────────────────
function createMainWindow() {
  if (mainWin) {
    if (lastOpenedDate && lastOpenedDate !== todayStr()) {
      lastOpenedDate = todayStr();
      mainWin.webContents.reload();
    }
    mainWin.show(); mainWin.focus(); return;
  }

  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const floatPos = floatWin ? floatWin.getPosition() : [sw - 116, 16];
  const [winX, winY] = calcMainPos(floatPos[0], floatPos[1]);

  mainWin = new BrowserWindow({
    width: WIN_W, height: Math.min(WIN_H, sh - winY - 8),
    minWidth: 400, minHeight: 480,
    x: winX, y: winY,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#FAF9F6',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });

  lastOpenedDate = todayStr();
  mainWin.loadFile(path.join(__dirname, '../app/index.html'));
  mainWin.on('closed', () => { mainWin = null; });
}

// ── IPC ───────────────────────────────────────────────────────
ipcMain.handle('get-float-pos', () => floatWin ? floatWin.getPosition() : [0, 0]);

ipcMain.on('set-float-pos', (_, x, y) => {
  const fx = Math.round(x), fy = Math.round(y);
  if (floatWin) floatWin.setPosition(fx, fy);
  if (mainWin) { const [wx, wy] = calcMainPos(fx, fy); mainWin.setPosition(wx, wy); }
});

ipcMain.on('toggle-main', () => {
  if (mainWin && mainWin.isVisible()) mainWin.hide();
  else createMainWindow();
});

ipcMain.on('update-float-timer', (_, data) => {
  if (!floatWin) return;
  const hasTimer = data && data.remaining > 0;
  const newH = hasTimer ? 96 : 48;
  const [fx, fy] = floatWin.getPosition();
  floatWin.setSize(96, newH);
  floatWin.setPosition(fx, fy);
  floatWin.webContents.send('float-timer', data);
});

// 토큰 IPC
ipcMain.handle('get-token', async () => {
  const token = await getValidToken();
  return token ? { access_token: token.access_token, user_id: token.user_id, email: token.email } : null;
});
ipcMain.handle('open-auth', () => { openAuthWindow(); });
ipcMain.handle('clear-token', () => { clearToken(); });

// Apple Notes 동기화
ipcMain.handle('sync-notes', async (_, { date, content, todos }) => {
  const title    = `${date} 체크리스트 메모`;
  const tmpBody  = `/tmp/checkmate-note-${Date.now()}.html`;
  const tmpScript = `/tmp/checkmate-sync.scpt`;
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const todoHtml = todos.map(t =>
    t.done ? `<div><s>○ ${esc(t.label)}</s></div>` : `<div>○ ${esc(t.label)}</div>`
  ).join('');
  const memoHtml = (content || '').trim()
    .split('\n').map(l => `<div>${esc(l) || '<br>'}</div>`).join('');
  const body = `<div><b>${esc(title)}</b></div><div><br></div>${todoHtml}${memoHtml}`;
  fs.writeFileSync(tmpBody, body, 'utf-8');
  const script = `
set noteBody to do shell script "cat " & quoted form of "${tmpBody}"
tell application "Notes"
  if not (exists folder "체크리스트" of default account) then
    make new folder at default account with properties {name: "체크리스트"}
  end if
  tell folder "체크리스트" of default account
    set matchNote to missing value
    repeat with n in every note
      if name of n is "${title}" then set matchNote to n
    end repeat
    if matchNote is missing value then
      make new note with properties {body: noteBody}
    else
      set body of matchNote to noteBody
    end if
  end tell
end tell
`;
  fs.writeFileSync(tmpScript, script, 'utf-8');
  try { execSync(`osascript "${tmpScript}"`); return { ok: true }; }
  catch (e) { return { ok: false, error: e.message }; }
});

// ── 앱 초기화 ─────────────────────────────────────────────────
app.whenReady().then(() => {
  createFloatWindow();
  app.on('activate', () => { if (!floatWin) createFloatWindow(); });
});

app.on('window-all-closed', () => { if (floatWin === null) app.quit(); });
