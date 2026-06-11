// 체크리스트 로컬 서버
// 실행: node 40-personal/checklist-server.js
// 접속: http://localhost:3737

const http  = require('http');
const https = require('https');
const fs    = require('fs');
const path  = require('path');
const { execSync } = require('child_process');

const PORT          = 3737;
const DIR           = __dirname;
const WORKSPACE     = path.resolve(DIR, '..');
const HTML_FILE     = path.join(DIR, '2026-05-12-today-checklist.html');
const TRACKING_FILE = path.join(DIR, '44-이직현황.md');
const BRAND_FILE    = path.join(WORKSPACE, '50-resources/소비재-브랜드-리스트.md');
const HISTORY_FILE  = path.join(DIR, 'checklist-history.json');
const TODOS_FILE    = path.join(DIR, 'checklist-todos.json');
const GROUPS_DIR    = path.join(DIR, 'groups');
const NOTES_IDS_FILE  = path.join(DIR, 'checklist-notes-ids.json');
const GCAL_TOKEN_FILE = path.join(DIR, 'checklist-gcal-token.json');
const GCAL_REDIRECT   = `http://localhost:${PORT}/api/auth/google/callback`;
const GCAL_SCOPE      = 'https://www.googleapis.com/auth/calendar';

// .env 로드
;(function loadEnv() {
  try {
    fs.readFileSync(path.join(DIR, '.env'), 'utf-8').split('\n').forEach(line => {
      const idx = line.indexOf('=');
      if (idx > 0) process.env[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    });
  } catch(e) {}
})();

function pad(n) { return String(n).padStart(2, '0'); }
function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`;
}

function loadNoteIds() {
  try {
    if (fs.existsSync(NOTES_IDS_FILE)) return JSON.parse(fs.readFileSync(NOTES_IDS_FILE, 'utf-8'));
  } catch(e) {}
  return {};
}

function saveNoteId(dateStr, id) {
  const ids = loadNoteIds();
  ids[dateStr] = id;
  fs.writeFileSync(NOTES_IDS_FILE, JSON.stringify(ids, null, 2), 'utf-8');
}

function toNotesHtml(title, content, todos) {
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  let todoHtml = '';
  if (todos && todos.length > 0) {
    // Notes 네이티브 체크박스 형식 — 앱에서 직접 체크/해제 가능
    const items = todos.map(t => {
      const checked = t.done ? ' Apple-checked' : '';
      return `<ul class="Apple-dash-list${checked}"><li class="Apple-dash-list-item${checked}">${esc(t.label)}</li></ul>`;
    }).join('');
    todoHtml = items + '<div><br></div>';
  }

  const memoHtml = content.trim()
    ? content.split('\n').map(l => l === '' ? '<div><br></div>' : `<div>${esc(l)}</div>`).join('')
    : '';

  return `<div><b>${esc(title)}</b></div><div><br></div>${todoHtml}${memoHtml}`;
}

function syncToNotes(dateStr, content, todos) {
  const title = `${dateStr} 체크리스트 메모`;
  const contentFile = '/tmp/checklist-note-content.txt';
  fs.writeFileSync(contentFile, toNotesHtml(title, content, todos), 'utf-8');

  const existingId = loadNoteIds()[dateStr] || '';

  const script = `
set contentFile to "/tmp/checklist-note-content.txt"
set noteBody to do shell script "cat " & quoted form of contentFile
set existingId to "${existingId}"

tell application "Notes"
  if not (exists folder "체크리스트" of default account) then
    make new folder at default account with properties {name: "체크리스트"}
  end if
  tell folder "체크리스트" of default account
    set targetNote to missing value
    if existingId is not "" then
      try
        set targetNote to note id existingId
      end try
    end if
    if targetNote is missing value then
      set targetNote to make new note with properties {body: noteBody}
    else
      set body of targetNote to noteBody
    end if
    return id of targetNote
  end tell
end tell
`;
  const tmpFile = '/tmp/checklist-note-sync.scpt';
  fs.writeFileSync(tmpFile, script, 'utf-8');
  try {
    const result = execSync(`osascript ${tmpFile}`).toString().trim();
    if (result) saveNoteId(dateStr, result);
    console.log(`[${new Date().toLocaleTimeString()}] 메모 앱 동기화: ${title}`);
  } catch(e) {
    console.error('Notes 동기화 오류:', e.message);
  }
}

function sanitizeFilename(name) {
  return name.replace(/[/\\:*?"<>|.]/g, '-').trim();
}

function groupFilePath(groupName) {
  if (!fs.existsSync(GROUPS_DIR)) fs.mkdirSync(GROUPS_DIR);
  return path.join(GROUPS_DIR, sanitizeFilename(groupName) + '.md');
}

function createGroupFile(groupName) {
  const filePath = groupFilePath(groupName);
  if (fs.existsSync(filePath)) return filePath;
  const today = todayStr();
  const content = `# ${groupName}\n\n생성일: ${today}\n\n| 제목 | 추가 작성 | URL | 날짜 |\n|------|----------|-----|------|\n`;
  fs.writeFileSync(filePath, content, 'utf-8');
  try {
    execSync(`git -C "${WORKSPACE}" add "${filePath}"`);
    execSync(`git -C "${WORKSPACE}" commit -m "feat: ${groupName} 그룹 파일 생성 (${today})"`);
    console.log(`[${new Date().toLocaleTimeString()}] 그룹 파일 생성: ${groupName}.md`);
  } catch(e) { console.error('Git 오류(그룹 생성):', e.message); }
  return filePath;
}

function syncGroupFile(groupName, items) {
  const filePath = groupFilePath(groupName);
  const today = todayStr();
  const rows = items.map(c => {
    const urlCell = c.url ? `[URL](${c.url})` : '';
    return `| ${c.name} | ${c.role || '-'} | ${urlCell} | ${c.date || today} |`;
  });
  const tableBody = rows.length > 0 ? rows.join('\n') : '| | | | |';
  const content = `# ${groupName}\n\n마지막 업데이트: ${today}\n\n| 제목 | 추가 작성 | URL | 날짜 |\n|------|----------|-----|------|\n${tableBody}\n`;
  fs.writeFileSync(filePath, content, 'utf-8');
  try {
    execSync(`git -C "${WORKSPACE}" add "${filePath}"`);
    const diff = execSync(`git -C "${WORKSPACE}" diff --cached --stat 2>&1`).toString().trim();
    if (diff) {
      const names = items.map(c => c.name).join(', ').slice(0, 50);
      execSync(`git -C "${WORKSPACE}" commit -m "feat: [${groupName}] 업데이트 (${today}) — ${names}"`);
      console.log(`[${new Date().toLocaleTimeString()}] 커밋 완료: [${groupName}]`);
    }
  } catch(e) { console.error(`Git 오류(${groupName}):`, e.message); }
}

// ── Google Calendar ──────────────────────────────────────────────────────────

function httpsJSON(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch(e) { resolve({}); } });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

function loadGcalTokens() {
  try { return JSON.parse(fs.readFileSync(GCAL_TOKEN_FILE, 'utf-8')); } catch(e) { return {}; }
}

function saveGcalTokens(tokens) {
  fs.writeFileSync(GCAL_TOKEN_FILE, JSON.stringify(tokens, null, 2), 'utf-8');
}

async function getAccessToken() {
  const tokens = loadGcalTokens();
  if (!tokens.refresh_token) return null;
  if (tokens.access_token && tokens.expires_at && Date.now() < tokens.expires_at - 60000) {
    return tokens.access_token;
  }
  const body = new URLSearchParams({
    client_id: process.env.GOOGLE_CLIENT_ID,
    client_secret: process.env.GOOGLE_CLIENT_SECRET,
    refresh_token: tokens.refresh_token,
    grant_type: 'refresh_token',
  }).toString();
  const result = await httpsJSON({
    hostname: 'oauth2.googleapis.com', path: '/token', method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) },
  }, body);
  if (result.access_token) {
    tokens.access_token = result.access_token;
    tokens.expires_at   = Date.now() + result.expires_in * 1000;
    saveGcalTokens(tokens);
    return tokens.access_token;
  }
  return null;
}

async function gcalAPI(method, apiPath, body) {
  const accessToken = await getAccessToken();
  if (!accessToken) return null;
  const bodyStr = body ? JSON.stringify(body) : undefined;
  const options = {
    hostname: 'www.googleapis.com',
    path: apiPath,
    method,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      ...(bodyStr ? { 'Content-Length': Buffer.byteLength(bodyStr) } : {}),
    },
  };
  return httpsJSON(options, bodyStr);
}

function saveHistory(date, companies, todos) {
  let history = {};
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'));
    }
  } catch(e) {}
  history[date] = { companies, todos: todos || [] };
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2), 'utf-8');
}

function syncToMarkdown(companies) {
  let content = fs.readFileSync(TRACKING_FILE, 'utf-8');
  const today = todayStr();

  const rows = companies.map(c => {
    const status = c.applied ? '✅' : '⏳';
    const bigo   = c.url ? `[공고 보기](${c.url})` : '';
    return `| ${status} ${c.name} | ${c.role || '-'} | ${today} | ${bigo} |`;
  });

  const tableBody  = rows.length > 0 ? rows.join('\n') : '| | | | |';
  const newSection = `## 앞으로 지원 예정\n\n| 회사 | 포지션 | 예정일 | 비고 |\n|------|--------|--------|------|\n${tableBody}\n`;

  const marker = '## 앞으로 지원 예정';
  const idx = content.indexOf(marker);
  if (idx !== -1) {
    content = content.slice(0, idx) + newSection;
  } else {
    content = content.trimEnd() + '\n\n' + newSection;
  }

  fs.writeFileSync(TRACKING_FILE, content, 'utf-8');
  syncBrandList(companies, today);

  try {
    execSync(`git -C "${WORKSPACE}" add "${TRACKING_FILE}" "${BRAND_FILE}"`);
    const diff = execSync(`git -C "${WORKSPACE}" diff --cached --stat 2>&1`).toString().trim();
    if (diff) {
      const names = companies.map(c => c.name).join(', ') || '없음';
      execSync(`git -C "${WORKSPACE}" commit -m "feat: 지원 목록 업데이트 (${today}) — ${names.slice(0, 50)}"`);
      console.log(`[${new Date().toLocaleTimeString()}] 커밋 완료: ${names}`);
    }
  } catch (e) {
    console.error('Git 오류:', e.message);
  }
}

function syncBrandList(companies, today) {
  let content = fs.readFileSync(BRAND_FILE, 'utf-8');

  // 기존 브랜드명 추출 (중복 방지)
  const existing = new Set();
  content.split('\n').forEach(line => {
    const m = line.match(/^\| (.+?) \|/);
    if (m && m[1] !== '브랜드') existing.add(m[1].trim());
  });

  // 신규 브랜드만 필터
  const newBrands = companies.filter(c => !existing.has(c.name.trim()));
  if (newBrands.length === 0) return;

  // 날짜 업데이트
  content = content.replace(/마지막 업데이트: .+/, `마지막 업데이트: ${today}`);

  // 새 행 추가
  const newRows = newBrands.map(c => {
    const urlCell = c.url ? `[공고 보기](${c.url})` : '';
    return `| ${c.name} | ${urlCell} | ${today} |`;
  }).join('\n');

  content = content.trimEnd() + '\n' + newRows + '\n';
  fs.writeFileSync(BRAND_FILE, content, 'utf-8');
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    try {
      const html = fs.readFileSync(HTML_FILE, 'utf-8');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.setHeader('Cache-Control', 'no-store');
      res.writeHead(200);
      res.end(html);
    } catch (e) {
      res.writeHead(500);
      res.end('HTML 파일 로드 실패: ' + e.message);
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/api/history') {
    try {
      const history = fs.existsSync(HISTORY_FILE)
        ? JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'))
        : {};
      res.setHeader('Content-Type', 'application/json');
      res.writeHead(200);
      res.end(JSON.stringify(history));
    } catch(e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/api/todos') {
    try {
      const data = fs.existsSync(TODOS_FILE)
        ? JSON.parse(fs.readFileSync(TODOS_FILE, 'utf-8'))
        : { todos: [], updatedAt: null };
      res.setHeader('Content-Type', 'application/json');
      res.writeHead(200);
      res.end(JSON.stringify(data));
    } catch(e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  if (req.method === 'POST' && req.url === '/api/todos') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { todos = [] } = JSON.parse(body);
        const data = { todos, updatedAt: new Date().toISOString() };
        fs.writeFileSync(TODOS_FILE, JSON.stringify(data, null, 2), 'utf-8');
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true }));
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.method === 'POST' && req.url === '/api/sync-memo') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { date, content, todos } = JSON.parse(body);
        if (!date) throw new Error('date required');
        syncToNotes(date, content || '', todos || []);
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true }));
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.method === 'GET' && req.url === '/api/sync-files') {
    try {
      const files = ['40-personal/44-이직현황.md'];
      if (fs.existsSync(GROUPS_DIR)) {
        fs.readdirSync(GROUPS_DIR)
          .filter(f => f.endsWith('.md'))
          .forEach(f => files.push(`40-personal/groups/${f}`));
      }
      res.setHeader('Content-Type', 'application/json');
      res.writeHead(200);
      res.end(JSON.stringify({ files }));
    } catch(e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  if (req.method === 'POST' && req.url === '/api/create-group') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { name } = JSON.parse(body);
        if (!name) throw new Error('name required');
        const filePath = createGroupFile(name);
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, file: path.relative(WORKSPACE, filePath) }));
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.method === 'POST' && req.url === '/api/sync') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { companies = [], todos = [] } = JSON.parse(body);

        // 그룹별 분리
        const byGroup = {};
        companies.forEach(c => {
          const g = c.group || '회사리스트';
          if (!byGroup[g]) byGroup[g] = [];
          byGroup[g].push(c);
        });

        // 회사리스트 → 기존 이직현황.md 동작
        const syncedFiles = [];
        const mainList = byGroup['회사리스트'] || [];
        if (mainList.length > 0) {
          syncToMarkdown(mainList);
          syncedFiles.push('40-personal/44-이직현황.md');
        }

        // 나머지 그룹 → groups/{그룹명}.md
        Object.entries(byGroup).forEach(([groupName, items]) => {
          if (groupName !== '회사리스트') {
            syncGroupFile(groupName, items);
            syncedFiles.push(`40-personal/groups/${sanitizeFilename(groupName)}.md`);
          }
        });

        saveHistory(todayStr(), companies, todos);
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, files: syncedFiles }));
      } catch (e) {
        console.error('Sync 오류:', e.message);
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // ── Google Calendar Auth ─────────────────────────────────────────────────
  if (req.method === 'GET' && req.url === '/api/auth/google') {
    const url = 'https://accounts.google.com/o/oauth2/v2/auth?' + new URLSearchParams({
      client_id: process.env.GOOGLE_CLIENT_ID,
      redirect_uri: GCAL_REDIRECT,
      response_type: 'code',
      scope: GCAL_SCOPE,
      access_type: 'offline',
      prompt: 'consent',
    });
    res.writeHead(302, { Location: url });
    res.end();
    return;
  }

  if (req.method === 'GET' && req.url.startsWith('/api/auth/google/callback')) {
    const code = new URL(`http://localhost${req.url}`).searchParams.get('code');
    try {
      const body = new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID,
        client_secret: process.env.GOOGLE_CLIENT_SECRET,
        code, redirect_uri: GCAL_REDIRECT,
        grant_type: 'authorization_code',
      }).toString();
      const result = await httpsJSON({
        hostname: 'oauth2.googleapis.com', path: '/token', method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) },
      }, body);
      if (result.refresh_token) {
        saveGcalTokens({ ...result, expires_at: Date.now() + result.expires_in * 1000 });
        console.log('[GCal] 인증 완료 — 토큰 저장됨');
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end('<script>window.close();</script><p>✅ Google Calendar 연동 완료! 창을 닫으세요.</p>');
      } else {
        res.writeHead(400);
        res.end('토큰 교환 실패: ' + JSON.stringify(result));
      }
    } catch(e) {
      res.writeHead(500);
      res.end(e.message);
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/api/auth/status') {
    const tokens = loadGcalTokens();
    res.setHeader('Content-Type', 'application/json');
    res.writeHead(200);
    res.end(JSON.stringify({ authenticated: !!tokens.refresh_token }));
    return;
  }

  // ── Google Calendar Events ───────────────────────────────────────────────
  if (req.method === 'GET' && req.url.startsWith('/api/calendar/events')) {
    try {
      const params = new URL(`http://localhost${req.url}`).searchParams;
      const year  = parseInt(params.get('year')  || new Date().getFullYear());
      const month = parseInt(params.get('month') || new Date().getMonth() + 1);
      const timeMin = new Date(year, month - 1, 1).toISOString();
      const timeMax = new Date(year, month, 0, 23, 59, 59).toISOString();
      const query = new URLSearchParams({ timeMin, timeMax, singleEvents: 'true', orderBy: 'startTime', maxResults: '100' });
      const result = await gcalAPI('GET', `/calendar/v3/calendars/primary/events?${query}`);
      res.setHeader('Content-Type', 'application/json');
      res.writeHead(200);
      res.end(JSON.stringify({ events: result ? (result.items || []) : [], error: result?.error }));
    } catch(e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  if (req.method === 'POST' && req.url === '/api/calendar/events') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const { title, date, description } = JSON.parse(body);
        const event = {
          summary: title,
          description: description || '',
          start: { date },
          end:   { date },
        };
        const result = await gcalAPI('POST', '/calendar/v3/calendars/primary/events', event);
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, id: result?.id }));
      } catch(e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.method === 'DELETE' && req.url.startsWith('/api/calendar/events/')) {
    const eventId = decodeURIComponent(req.url.replace('/api/calendar/events/', ''));
    try {
      await gcalAPI('DELETE', `/calendar/v3/calendars/primary/events/${eventId}`);
      res.setHeader('Content-Type', 'application/json');
      res.writeHead(200);
      res.end(JSON.stringify({ ok: true }));
    } catch(e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  if (!fs.existsSync(GROUPS_DIR)) fs.mkdirSync(GROUPS_DIR);
  console.log(`\n체크리스트 서버 시작`);
  console.log(`  브라우저: http://localhost:${PORT}`);
  console.log(`  회사리스트 → 40-personal/44-이직현황.md`);
  console.log(`  기타 그룹  → 40-personal/groups/{그룹명}.md`);
  console.log(`  그룹 생성/수정 시 자동 git commit\n`);
});
