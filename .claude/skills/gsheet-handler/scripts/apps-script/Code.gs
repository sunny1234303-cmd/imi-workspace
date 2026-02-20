/**
 * Code.gs - 메인 프로그램
 */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('키워드 분석')
    .addItem('키워드 검색량 분석', 'showKeywordDialog')
    .addItem('키워드 트렌드 분석', 'showTrendDialog')
    .addSeparator()
    .addItem('대시보드 새로고침', 'refreshDashboard')
    .addSeparator()
    .addItem('API 설정', 'showSettingsDialog')
    .addToUi();
}

function showKeywordDialog() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        h2 { color: #1a73e8; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; }
        .checkbox-group input { width: auto; }
        .checkbox-group label { margin: 0; }
        .hint { font-size: 12px; color: #666; margin-top: 5px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #4285f4; color: white; }
        .btn-secondary { background: #f1f3f4; color: #5f6368; }
        .buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
      </style>
    </head>
    <body>
      <h2>키워드 검색량 분석</h2>
      <div class="form-group">
        <label>키워드</label>
        <input type="text" id="keywords" placeholder="예: 스킨케어, 화장품">
        <div class="hint">쉼표로 구분 (최대 5개)</div>
      </div>
      <div class="form-group">
        <label>카테고리 (선택)</label>
        <input type="text" id="category" placeholder="예: 뷰티, 식품">
      </div>
      <div class="form-group">
        <div class="checkbox-group">
          <input type="checkbox" id="includeRelated">
          <label for="includeRelated">연관 키워드 포함</label>
        </div>
      </div>
      <div class="form-group">
        <div class="checkbox-group">
          <input type="checkbox" id="clearExisting" checked>
          <label for="clearExisting">기존 데이터 초기화</label>
        </div>
      </div>
      <div class="buttons">
        <button class="btn btn-secondary" onclick="google.script.host.close()">취소</button>
        <button class="btn btn-primary" onclick="submitKeyword()">분석 시작</button>
      </div>
      <script>
        function submitKeyword() {
          const keywords = document.getElementById('keywords').value.trim();
          const category = document.getElementById('category').value.trim() || '미분류';
          const includeRelated = document.getElementById('includeRelated').checked;
          const clearExisting = document.getElementById('clearExisting').checked;
          if (!keywords) { alert('키워드를 입력해주세요.'); return; }
          document.querySelector('.btn-primary').disabled = true;
          document.querySelector('.btn-primary').textContent = '분석 중...';
          google.script.run
            .withSuccessHandler(function(r) { alert(r); google.script.host.close(); })
            .withFailureHandler(function(e) { alert('오류: ' + e.message); document.querySelector('.btn-primary').disabled = false; document.querySelector('.btn-primary').textContent = '분석 시작'; })
            .analyzeKeywords(keywords, includeRelated, category, clearExisting);
        }
      </script>
    </body>
    </html>
  `).setWidth(400).setHeight(350);
  SpreadsheetApp.getUi().showModalDialog(html, '키워드 검색량 분석');
}

function showTrendDialog() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; padding: 20px; margin: 0; }
        h2 { color: #1a73e8; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; }
        .checkbox-group input { width: auto; }
        .checkbox-group label { margin: 0; }
        .hint { font-size: 12px; color: #666; margin-top: 5px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #4285f4; color: white; }
        .btn-secondary { background: #f1f3f4; color: #5f6368; }
        .buttons { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
      </style>
    </head>
    <body>
      <h2>키워드 트렌드 분석</h2>
      <div class="form-group">
        <label>키워드</label>
        <input type="text" id="keywords" placeholder="예: 스킨케어">
        <div class="hint">쉼표로 구분 (최대 5개)</div>
      </div>
      <div class="form-group">
        <label>카테고리 (선택)</label>
        <input type="text" id="category" placeholder="예: 뷰티">
      </div>
      <div class="form-group">
        <label>분석 기간</label>
        <select id="days">
          <option value="7">최근 7일</option>
          <option value="30" selected>최근 30일</option>
          <option value="90">최근 90일</option>
          <option value="180">최근 180일</option>
          <option value="365">최근 1년</option>
        </select>
      </div>
      <div class="form-group">
        <label>디바이스</label>
        <select id="device">
          <option value="">전체</option>
          <option value="pc">PC</option>
          <option value="mo">모바일</option>
        </select>
      </div>
      <div class="form-group">
        <div class="checkbox-group">
          <input type="checkbox" id="clearExisting" checked>
          <label for="clearExisting">기존 데이터 초기화</label>
        </div>
      </div>
      <div class="buttons">
        <button class="btn btn-secondary" onclick="google.script.host.close()">취소</button>
        <button class="btn btn-primary" onclick="submitTrend()">분석 시작</button>
      </div>
      <script>
        function submitTrend() {
          const keywords = document.getElementById('keywords').value.trim();
          const category = document.getElementById('category').value.trim() || '미분류';
          const days = parseInt(document.getElementById('days').value);
          const device = document.getElementById('device').value;
          const clearExisting = document.getElementById('clearExisting').checked;
          if (!keywords) { alert('키워드를 입력해주세요.'); return; }
          document.querySelector('.btn-primary').disabled = true;
          document.querySelector('.btn-primary').textContent = '분석 중...';
          google.script.run
            .withSuccessHandler(function(r) { alert(r); google.script.host.close(); })
            .withFailureHandler(function(e) { alert('오류: ' + e.message); document.querySelector('.btn-primary').disabled = false; document.querySelector('.btn-primary').textContent = '분석 시작'; })
            .analyzeTrend(keywords, days, device, category, clearExisting);
        }
      </script>
    </body>
    </html>
  `).setWidth(400).setHeight(420);
  SpreadsheetApp.getUi().showModalDialog(html, '키워드 트렌드 분석');
}

function analyzeKeywords(keywords, includeRelated, category, clearExisting) {
  const keys = getApiKeys();
  if (!keys.NAVER_AD_ACCESS_LICENSE || !keys.NAVER_AD_SECRET_KEY || !keys.NAVER_AD_CUSTOMER_ID) {
    throw new Error('API 설정이 필요합니다. 메뉴 > API 설정');
  }
  const timestamp = new Date().getTime().toString();
  const uri = '/keywordstool';
  const signature = generateSignature(timestamp, 'GET', uri, keys.NAVER_AD_SECRET_KEY);
  const params = { hintKeywords: keywords, showDetail: '1' };
  if (includeRelated) params.includeHintKeywords = '1';
  const queryString = Object.entries(params).map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v)).join('&');
  const url = CONFIG.SEARCHAD_URL + '?' + queryString;
  const options = {
    method: 'GET',
    headers: { 'X-Timestamp': timestamp, 'X-API-KEY': keys.NAVER_AD_ACCESS_LICENSE, 'X-Customer': keys.NAVER_AD_CUSTOMER_ID, 'X-Signature': signature, 'Content-Type': 'application/json' },
    muteHttpExceptions: true
  };
  const response = UrlFetchApp.fetch(url, options);
  if (response.getResponseCode() !== 200) throw new Error('API 오류: ' + response.getContentText());
  const result = JSON.parse(response.getContentText());
  if (!result.keywordList || result.keywordList.length === 0) return '검색 결과가 없습니다.';

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.RAW_KEYWORD_TAB);
  const headers = ['키워드', 'PC검색량', '모바일검색량', '총검색량', 'PC클릭수', '모바일클릭수', 'PC클릭률', '모바일클릭률', '경쟁강도', '노출광고수', '카테고리', '수집일시'];

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.RAW_KEYWORD_TAB);
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold').setBackground('#e3f2fd');
  } else if (clearExisting) {
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }

  const collectedAt = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  const rows = [];
  for (const kw of result.keywordList) {
    let pcQc = kw.monthlyPcQcCnt || 0;
    let moQc = kw.monthlyMobileQcCnt || 0;
    if (typeof pcQc === 'string') pcQc = pcQc.includes('< 10') ? 10 : parseInt(pcQc.replace(/,/g, ''));
    if (typeof moQc === 'string') moQc = moQc.includes('< 10') ? 10 : parseInt(moQc.replace(/,/g, ''));
    rows.push([kw.relKeyword || '', pcQc, moQc, pcQc + moQc, kw.monthlyAvePcClkCnt || 0, kw.monthlyAveMobileClkCnt || 0, kw.monthlyAvePcCtr || 0, kw.monthlyAveMobileCtr || 0, kw.compIdx || '-', kw.plAvgDepth || 0, category, collectedAt]);
  }
  sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, headers.length).setValues(rows);
  updateDashboard();
  return '완료: ' + rows.length + '개 키워드 분석됨';
}

function analyzeTrend(keywords, days, device, category, clearExisting) {
  const keys = getApiKeys();
  if (!keys.NAVER_CLIENT_ID || !keys.NAVER_CLIENT_SECRET) throw new Error('API 설정이 필요합니다.');
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  const keywordList = keywords.split(',').map(function(k) { return k.trim(); }).slice(0, 5);
  const keywordGroups = keywordList.map(function(kw) { return { groupName: kw, keywords: [kw] }; });
  const body = { startDate: Utilities.formatDate(startDate, 'Asia/Seoul', 'yyyy-MM-dd'), endDate: Utilities.formatDate(endDate, 'Asia/Seoul', 'yyyy-MM-dd'), timeUnit: 'date', keywordGroups: keywordGroups };
  if (device) body.device = device;
  const options = { method: 'POST', headers: { 'X-Naver-Client-Id': keys.NAVER_CLIENT_ID, 'X-Naver-Client-Secret': keys.NAVER_CLIENT_SECRET, 'Content-Type': 'application/json' }, payload: JSON.stringify(body), muteHttpExceptions: true };
  const response = UrlFetchApp.fetch(CONFIG.DATALAB_URL, options);
  if (response.getResponseCode() !== 200) throw new Error('API 오류: ' + response.getContentText());
  const result = JSON.parse(response.getContentText());
  if (!result.results || result.results.length === 0) return '검색 결과가 없습니다.';

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.RAW_TREND_TAB);
  const headers = ['키워드', '날짜', '검색지수', '카테고리', '수집일시'];
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.RAW_TREND_TAB);
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold').setBackground('#e3f2fd');
  } else if (clearExisting) {
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
  const collectedAt = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  const rows = [];
  for (var i = 0; i < result.results.length; i++) {
    var group = result.results[i];
    for (var j = 0; j < group.data.length; j++) {
      rows.push([group.title, group.data[j].period, group.data[j].ratio, category, collectedAt]);
    }
  }
  sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, headers.length).setValues(rows);
  updateDashboard();
  return '완료: ' + rows.length + '개 트렌드 데이터 수집됨';
}

function refreshDashboard() {
  updateDashboard();
  SpreadsheetApp.flush();
  SpreadsheetApp.getUi().alert('새로고침 완료');
}

function updateDashboard() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let dashboard = ss.getSheetByName('키워드 대시보드');
  if (!dashboard) {
    dashboard = ss.insertSheet('키워드 대시보드');
  }
  setupDashboard(dashboard);
}

function setupDashboard(sheet) {
  // 기존 내용 클리어
  sheet.clear();

  // 필터 영역 (A1~C4)
  sheet.getRange('A1').setValue('📊 필터').setFontWeight('bold').setFontSize(12);
  sheet.getRange('A2').setValue('카테고리:').setFontWeight('bold');
  sheet.getRange('A3').setValue('수집일시:').setFontWeight('bold');
  sheet.getRange('B2').setValue('전체');
  sheet.getRange('B3').setValue('전체');
  sheet.getRange('A1:C4').setBackground('#e3f2fd');

  // 핵심 요약 (A6~C14)
  sheet.getRange('A6').setValue('📈 핵심 요약').setFontWeight('bold').setFontSize(12);
  sheet.getRange('A7').setValue('총 키워드 수');
  sheet.getRange('A8').setValue('평균 검색량');
  sheet.getRange('A9').setValue('검색량 중앙값');
  sheet.getRange('B7').setFormula('=IF(B2="전체",COUNTA(Raw_키워드!A:A)-1,COUNTIF(Raw_키워드!K:K,B2))');
  sheet.getRange('B8').setFormula('=IFERROR(IF(B2="전체",ROUND(AVERAGE(Raw_키워드!D2:D),0),ROUND(AVERAGEIF(Raw_키워드!K:K,B2,Raw_키워드!D:D),0)),"-")');
  sheet.getRange('B9').setFormula('=IFERROR(ROUND(MEDIAN(Raw_키워드!D2:D),0),"-")');

  sheet.getRange('A11').setValue('📊 경쟁강도 분포').setFontWeight('bold').setFontSize(12);
  sheet.getRange('A12').setValue('높음');
  sheet.getRange('A13').setValue('중간');
  sheet.getRange('A14').setValue('낮음');
  sheet.getRange('B12').setFormula('=IF(B2="전체",COUNTIF(Raw_키워드!I:I,"높음"),COUNTIFS(Raw_키워드!I:I,"높음",Raw_키워드!K:K,B2))');
  sheet.getRange('B13').setFormula('=IF(B2="전체",COUNTIF(Raw_키워드!I:I,"중간"),COUNTIFS(Raw_키워드!I:I,"중간",Raw_키워드!K:K,B2))');
  sheet.getRange('B14').setFormula('=IF(B2="전체",COUNTIF(Raw_키워드!I:I,"낮음"),COUNTIFS(Raw_키워드!I:I,"낮음",Raw_키워드!K:K,B2))');
  sheet.getRange('C12').setFormula('=IFERROR(ROUND(B12/B7*100,0)&"%","-")');
  sheet.getRange('C13').setFormula('=IFERROR(ROUND(B13/B7*100,0)&"%","-")');
  sheet.getRange('C14').setFormula('=IFERROR(ROUND(B14/B7*100,0)&"%","-")');

  sheet.getRange('A6:C9').setBackground('#fff3e0');
  sheet.getRange('A11:C14').setBackground('#e8f5e9');

  // TOP 검색량 (G1~K17)
  sheet.getRange('G1').setValue('🔥 TOP 검색량 (상위 15)').setFontWeight('bold').setFontSize(12);
  sheet.getRange('G2').setFormula('=IFERROR(IF(B2="전체",QUERY(Raw_키워드!A:L,"SELECT A,B,C,D,I ORDER BY D DESC LIMIT 16",1),QUERY(Raw_키워드!A:L,"SELECT A,B,C,D,I WHERE K=\'"&B2&"\' ORDER BY D DESC LIMIT 16",1)),"데이터 없음")');

  // 황금 키워드 (G19~K35) - TOP 검색량 바로 아래
  sheet.getRange('G19').setValue('💎 황금 키워드 (검색량↑ 경쟁↓)').setFontWeight('bold').setFontSize(12);
  sheet.getRange('G20').setFormula('=IFERROR(IF(B2="전체",QUERY(Raw_키워드!A:L,"SELECT A,B,C,D,I WHERE I=\'낮음\' OR I=\'중간\' ORDER BY D DESC LIMIT 16",1),QUERY(Raw_키워드!A:L,"SELECT A,B,C,D,I WHERE (I=\'낮음\' OR I=\'중간\') AND K=\'"&B2&"\' ORDER BY D DESC LIMIT 16",1)),"데이터 없음")');

  // 경쟁 높음 주의 키워드 (A16~E32)
  sheet.getRange('A16').setValue('⚠️ 경쟁 높음 주의 키워드').setFontWeight('bold').setFontSize(12);
  sheet.getRange('A17').setFormula('=IFERROR(IF(B2="전체",QUERY(Raw_키워드!A:L,"SELECT A,D,I,J WHERE I=\'높음\' ORDER BY D DESC LIMIT 16",1),QUERY(Raw_키워드!A:L,"SELECT A,D,I,J WHERE I=\'높음\' AND K=\'"&B2&"\' ORDER BY D DESC LIMIT 16",1)),"데이터 없음")');

  // 드롭다운 설정
  const keywordSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.RAW_KEYWORD_TAB);
  const categories = ['전체'];
  const collectDates = ['전체'];

  if (keywordSheet && keywordSheet.getLastRow() > 1) {
    const kwData = keywordSheet.getRange(2, 11, keywordSheet.getLastRow() - 1, 2).getValues();
    kwData.forEach(function(row) {
      if (row[0] && categories.indexOf(row[0]) === -1) categories.push(row[0]);
      if (row[1]) { var d = row[1].toString().substring(0, 16); if (collectDates.indexOf(d) === -1) collectDates.push(d); }
    });
  }

  sheet.getRange('B2').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(categories.sort(), true).setAllowInvalid(false).build());
  sheet.getRange('B3').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(collectDates.sort().reverse(), true).setAllowInvalid(false).build());

  // 컬럼 너비
  sheet.setColumnWidth(1, 120);
  sheet.setColumnWidth(2, 100);
  sheet.setColumnWidth(3, 60);
  sheet.setColumnWidth(7, 150);
  sheet.setColumnWidth(8, 80);
  sheet.setColumnWidth(9, 80);
  sheet.setColumnWidth(10, 80);
  sheet.setColumnWidth(11, 60);
}
