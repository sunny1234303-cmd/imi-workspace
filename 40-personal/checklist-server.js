// 체크리스트 로컬 서버
// 실행: node 40-personal/checklist-server.js
// 접속: http://localhost:3737

const http = require('http');
const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT          = 3737;
const DIR           = __dirname;
const WORKSPACE     = path.resolve(DIR, '..');
const HTML_FILE     = path.join(DIR, '2026-05-12-today-checklist.html');
const TRACKING_FILE = path.join(DIR, '44-이직현황.md');
const BRAND_FILE    = path.join(WORKSPACE, '50-resources/소비재-브랜드-리스트.md');

function pad(n) { return String(n).padStart(2, '0'); }
function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`;
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

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    try {
      const html = fs.readFileSync(HTML_FILE, 'utf-8');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.writeHead(200);
      res.end(html);
    } catch (e) {
      res.writeHead(500);
      res.end('HTML 파일 로드 실패: ' + e.message);
    }
    return;
  }

  if (req.method === 'POST' && req.url === '/api/sync') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { companies = [] } = JSON.parse(body);
        syncToMarkdown(companies);
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true }));
      } catch (e) {
        console.error('Sync 오류:', e.message);
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`\n체크리스트 서버 시작`);
  console.log(`  브라우저: http://localhost:${PORT}`);
  console.log(`  연동 파일: 40-personal/44-이직현황.md`);
  console.log(`  회사 추가/변경 시 자동 git commit\n`);
});
