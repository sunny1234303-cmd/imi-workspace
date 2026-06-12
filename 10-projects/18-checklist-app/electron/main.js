const { app, BrowserWindow, screen, ipcMain, shell } = require('electron');
const path  = require('path');
const { execSync } = require('child_process');
const fs    = require('fs');

// ── 단일 인스턴스 강제 ────────────────────────────────────────────────
// 두 번째 실행 시 즉시 종료 — 이후 코드 전혀 실행 안 됨
if (!app.requestSingleInstanceLock()) {
  app.quit();
  process.exit(0);
}

let floatWin = null;
let mainWin  = null;
let lastOpenedDate = null;

// 두 번째 인스턴스가 실행됐을 때 첫 번째 창 포커스
app.on('second-instance', () => {
  if (mainWin) { mainWin.show(); mainWin.focus(); }
  else if (floatWin) { floatWin.show(); floatWin.focus(); }
});

// ── 플로팅 버튼 창 ────────────────────────────────────────────────────
function createFloatWindow() {
  floatWin = new BrowserWindow({
    width:       96,
    height:      48,
    frame:       false,
    transparent: true,
    alwaysOnTop: true,
    resizable:   false,
    hasShadow:   false,
    skipTaskbar: true,
    webPreferences: {
      preload:          path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    },
  });

  const { width } = screen.getPrimaryDisplay().workAreaSize;
  floatWin.setPosition(width - 116, 16);
  floatWin.loadFile(path.join(__dirname, 'float/index.html'));

  floatWin.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: false });
  floatWin.setAlwaysOnTop(true, 'floating');

  floatWin.on('closed', () => { floatWin = null; });
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

const WIN_W = 440;
const WIN_H = 720;

// 버튼 위치 기준으로 창 좌표 계산 (왼쪽/오른쪽 자동 판별)
function calcMainPos(fx, fy) {
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const isLeft = fx < sw / 2;
  const winX = isLeft
    ? Math.max(0, fx)                              // 버튼 왼쪽 정렬
    : Math.min(fx + 96 - WIN_W, sw - WIN_W);       // 버튼 오른쪽 정렬
  const winY = Math.min(fy + 48 + 8, sh - WIN_H - 8);
  return [Math.round(winX), Math.round(winY)];
}

// ── 메인 체크리스트 창 ────────────────────────────────────────────────
function createMainWindow() {
  if (mainWin) {
    if (lastOpenedDate && lastOpenedDate !== todayStr()) {
      lastOpenedDate = todayStr();
      mainWin.webContents.reload();
    }
    mainWin.show();
    mainWin.focus();
    return;
  }

  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const floatPos = floatWin ? floatWin.getPosition() : [sw - 116, 16];
  const [winX, winY] = calcMainPos(floatPos[0], floatPos[1]);

  mainWin = new BrowserWindow({
    width:         WIN_W,
    height:        Math.min(WIN_H, sh - winY - 8),
    minWidth:      400,
    minHeight:     480,
    x:             winX,
    y:             winY,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#FAF9F6',
    webPreferences: {
      preload:          path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    },
  });

  lastOpenedDate = todayStr();
  mainWin.loadFile(path.join(__dirname, '../app/index.html'));

  mainWin.on('closed', () => { mainWin = null; });
}

// ── IPC ───────────────────────────────────────────────────────────────
ipcMain.handle('get-float-pos', () => floatWin ? floatWin.getPosition() : [0, 0]);
ipcMain.on('set-float-pos', (_, x, y) => {
  const fx = Math.round(x), fy = Math.round(y);
  if (floatWin) floatWin.setPosition(fx, fy);
  if (mainWin) {
    const [wx, wy] = calcMainPos(fx, fy);
    mainWin.setPosition(wx, wy);
  }
});

ipcMain.on('toggle-main', () => {
  if (mainWin && mainWin.isVisible()) {
    mainWin.hide();
  } else {
    createMainWindow();
  }
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

// Apple Notes 동기화 (AppleScript via osascript)
ipcMain.handle('sync-notes', async (_, { date, content, todos }) => {
  const title    = `${date} 체크리스트 메모`;
  const tmpBody  = `/tmp/checkmate-note-${Date.now()}.html`;
  const tmpScript = `/tmp/checkmate-sync.scpt`;

  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  const todoHtml = todos.map(t => {
    const text = `○ ${esc(t.label)}`;
    return t.done
      ? `<div><s>${text}</s></div>`
      : `<div>${text}</div>`;
  }).join('');

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
      if name of n is "${title}" then
        set matchNote to n
        exit repeat
      end if
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
  try {
    execSync(`osascript "${tmpScript}"`);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
});

// ── 앱 초기화 ─────────────────────────────────────────────────────────
app.whenReady().then(() => {
  createFloatWindow();

  app.on('activate', () => {
    if (!floatWin) createFloatWindow();
  });
});

app.on('window-all-closed', () => {
  if (floatWin === null) app.quit();
});
