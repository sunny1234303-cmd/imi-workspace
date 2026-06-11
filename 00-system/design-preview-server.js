// 디자인 가이드 프리뷰 서버
// 실행: node 00-system/design-preview-server.js
// 접속: http://localhost:3800

const http = require('http');
const fs   = require('fs');
const path = require('path');

const PORT      = 3800;
const HTML_FILE = path.join(__dirname, 'design-preview.html');

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

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

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`\n디자인 프리뷰 서버 시작`);
  console.log(`  브라우저: http://localhost:${PORT}`);
  console.log(`  가이드:   00-system/design-guide.md\n`);
});
